import asyncio
import argparse
import logging
import sys

# Parse arguments first to check for --test mode before initializing settings
parser = argparse.ArgumentParser(description="LMS Telegram Bot")
parser.add_argument("--test", type=str, help="Run in test mode with the given command")
args, _ = parser.parse_known_args()

from config import settings
from registry import COMMAND_HANDLERS
import handlers.general.general  # Register command handlers
from services.lms import LMSClient
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

lms_client = LMSClient(base_url=settings.lms_api_base_url, api_key=settings.lms_api_key)


async def run_test_mode(command: str):
    """Runs the bot in test mode for a single command."""
    logging.basicConfig(level=logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    # Use the IntentRouter inside test mode if not starting with /
    if not command.startswith("/"):
        from services.router import IntentRouter

        router = IntentRouter(lms_client)
        try:
            response = await router.route(command)
            print(response)
        except Exception as e:
            print(f"An error occurred: {e}")
        sys.exit(0)

    command_parts = command.split()
    main_command = command_parts[0]
    args = command_parts[1] if len(command_parts) > 1 else None

    # Find the handler for the given command
    handler = COMMAND_HANDLERS.get(main_command)

    if handler:
        # Initialize the LMS client

        # Call the handler and print the result
        try:
            if main_command in ["/start", "/help"]:
                response = handler()
            elif args:
                response = await handler(lms_client, args)
            else:
                response = await handler(lms_client)
            print(response)
        except Exception as e:
            print(f"An error occurred: {e}")
            sys.exit(1)
    else:
        print(f"Unknown command. Use /help to see available commands.")
        sys.exit(0)


async def main():
    """Starts the bot."""
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    # Register command handlers
    async def start_command_handler(message: types.Message):
        """Handles the /start command."""
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="what labs are available?",
                        callback_data="what labs are available?",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="show me scores for lab 4",
                        callback_data="show me scores for lab 4",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="who are the top 5 students?",
                        callback_data="who are the top 5 students?",
                    )
                ],
            ]
        )
        await message.answer(COMMAND_HANDLERS["/start"](), reply_markup=keyboard)

    async def help_command_handler(message: types.Message):
        """Handles the /help command."""
        await message.answer(COMMAND_HANDLERS["/help"]())

    async def health_command_handler(message: types.Message):
        """Handles the /health command."""
        await message.answer(await COMMAND_HANDLERS["/health"](lms_client))

    async def labs_command_handler(message: types.Message):
        """Handles the /labs command."""
        await message.answer(await COMMAND_HANDLERS["/labs"](lms_client))

    async def scores_command_handler(message: types.Message):
        """Handles the /scores command."""
        if message.text is None:
            await message.answer("Please specify a lab ID. Usage: /scores <lab_id>")
            return
        command_parts = message.text.split(" ")
        lab_id = command_parts[1] if len(command_parts) > 1 else None
        if not lab_id:
            await message.answer("Please specify a lab ID. Usage: /scores <lab_id>")
            return
        await message.answer(await COMMAND_HANDLERS["/scores"](lms_client, lab_id))

    dp.message.register(start_command_handler, Command(commands=["start"]))
    dp.message.register(help_command_handler, Command(commands=["help"]))
    dp.message.register(health_command_handler, Command(commands=["health"]))
    dp.message.register(labs_command_handler, Command(commands=["labs"]))
    dp.message.register(scores_command_handler, Command(commands=["scores"]))

    from services.router import IntentRouter

    router = IntentRouter(lms_client)  # A simple handler for any text message

    async def echo_handler(message: types.Message) -> None:
        """Just prints the message text back."""
        try:
            if message.text:
                response = await router.route(message.text)
                await message.answer(response)
            else:
                await message.answer("Please send text.")
        except Exception as e:
            await message.answer(f"An error occurred: {e}")

    async def callback_query_handler(callback_query: types.CallbackQuery):
        """Hands callback queries from inline keyboards."""
        try:
            if callback_query.data and isinstance(
                callback_query.message, types.Message
            ):
                await callback_query.message.answer(
                    "Processing your request..."
                )  # Let user know
                response = await router.route(callback_query.data)
                await callback_query.message.answer(response)
                await callback_query.answer()
        except Exception as e:
            if isinstance(callback_query.message, types.Message):
                await callback_query.message.answer(f"An error occurred: {e}")

    dp.message.register(echo_handler)
    dp.callback_query.register(callback_query_handler)

    await dp.start_polling(bot)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LMS Telegram Bot")
    parser.add_argument(
        "--test", type=str, help="Run in test mode with the given command"
    )
    args = parser.parse_args()

    if args.test:
        # If --test argument is provided, run in test mode
        asyncio.run(run_test_mode(args.test))
    else:
        # Otherwise, start the bot normally
        asyncio.run(main())
