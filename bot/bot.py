import asyncio
import argparse
import logging
import sys

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from config import settings
from handlers.general import handle_start, handle_help, handle_health, handle_labs

# A dictionary to map commands to their handler functions
COMMAND_HANDLERS = {
    "/start": handle_start,
    "/help": handle_help,
    "/health": handle_health,
    "/labs": handle_labs,
}


async def run_test_mode(command: str):
    """Runs the bot in test mode for a single command."""
    logging.basicConfig(level=logging.INFO)
    logging.info(f"Running in test mode for command: {command}")

    # Find the handler for the given command
    handler = COMMAND_HANDLERS.get(command.split()[0])

    if handler:
        # Call the handler and print the result
        response = await handler()
        print(response)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


async def main():
    """Starts the bot."""
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    # Register command handlers
    async def start_command_handler(message: types.Message):
        """Handles the /start command."""
        await message.answer(await handle_start())

    async def help_command_handler(message: types.Message):
        """Handles the /help command."""
        await message.answer(await handle_help())

    async def health_command_handler(message: types.Message):
        """Handles the /health command."""
        await message.answer(await handle_health())

    async def labs_command_handler(message: types.Message):
        """Handles the /labs command."""
        await message.answer(await handle_labs())

    dp.message.register(start_command_handler, Command(commands=["start"]))
    dp.message.register(help_command_handler, Command(commands=["help"]))
    dp.message.register(health_command_handler, Command(commands=["health"]))
    dp.message.register(labs_command_handler, Command(commands=["labs"]))

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
