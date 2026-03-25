import httpx
from registry import COMMAND_HANDLERS
from services.lms import LMSClient


from typing import Optional


def handle_start() -> str:
    """Handles the /start command."""
    return "Welcome to the LMS Bot! Use /help to see available commands."


def handle_help() -> str:
    """Handles the /help command."""
    return "Available commands:\n/start - Welcome message\n/help - This message\n/health - Check backend status\n/labs - List available labs\n/scores <lab> - Per-task pass rates"


async def handle_health(lms_client: LMSClient) -> str:
    """Handles the /health command."""
    return await lms_client.get_health()


async def handle_labs(lms_client: LMSClient) -> str:
    """Handles the /labs command."""
    try:
        labs = await lms_client.get_labs()
        if not labs:
            return "No labs available."
        lab_list = "\n".join(
            f"- {lab['name']} — {lab['title']}"
            for lab in sorted(labs, key=lambda x: x["name"])
            if lab["type"] == "lab"
        )
        return f"Available labs:\n{lab_list}"
    except httpx.ConnectError as e:
        return f"Backend error: connection refused ({e.request.url}). Check that the services are running."
    except httpx.HTTPStatusError as e:
        return f"Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."
    except Exception as e:
        return f"Backend error: {e}"


async def handle_scores(lms_client: LMSClient, lab_id: Optional[str] = None) -> str:
    """Handles the /scores command."""
    if not lab_id:
        return "Please specify a lab ID. Usage: /scores <lab_id>"
    try:
        scores = await lms_client.get_scores(lab_id)
        if not scores:
            return f"No scores available for {lab_id}."

        # Find the lab title
        labs = await lms_client.get_labs()
        lab_title = ""
        for lab in labs:
            if lab["name"] == lab_id:
                lab_title = lab["title"]
                break

        score_list = "\n".join(
            f"- {score['task_title']}: {score['pass_rate']:.1f}% ({score['attempts']} attempts)"
            for score in scores
        )
        return f"Pass rates for {lab_title}:\n{score_list}"
    except httpx.ConnectError as e:
        return f"Backend error: connection refused ({e.request.url}). Check that the services are running."
    except httpx.HTTPStatusError as e:
        return f"Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."
    except Exception as e:
        return f"Backend error: {e}"


COMMAND_HANDLERS["/start"] = handle_start
COMMAND_HANDLERS["/help"] = handle_help
COMMAND_HANDLERS["/health"] = handle_health
COMMAND_HANDLERS["/labs"] = handle_labs
COMMAND_HANDLERS["/scores"] = handle_scores
