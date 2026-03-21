async def handle_start() -> str:
    """Handles the /start command."""
    return "Welcome to the LMS Bot! Use /help to see available commands."


async def handle_help() -> str:
    """Handles the /help command."""
    return "Available commands:\n/start - Welcome message\n/help - This message\n/health - Check backend status\n/labs - List available labs"


async def handle_health() -> str:
    """Handles the /health command."""
    # This will be implemented in Task 2 to call the backend.
    return "Backend status: OK (Not implemented yet)"


async def handle_labs() -> str:
    """Handles the /labs command."""
    # This will be implemented in Task 2.
    return "Available labs: (Not implemented yet)"
