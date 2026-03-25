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
    logging.basicConfig(level=logging.INFO)
    # logging.info(f"Running in test mode for command: {command}")

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
        await message.answer(COMMAND_HANDLERS["/start"]())

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

    # A simple handler for any text message
    async def echo_handler(message: types.Message) -> None:
        """Just prints the message text back."""
        try:
            await message.answer(
                "Unknown command. Use /help to see available commands."
            )
        except TypeError:
            await message.answer("An error occurred.")

    dp.message.register(echo_handler)

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
