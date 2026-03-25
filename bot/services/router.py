import sys
import json
import httpx
from typing import List, Dict, Any
from services.lms import LMSClient
from config import settings

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_items",
            "description": "Get a list of all available labs and tasks. Useful to know what labs are available.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_learners",
            "description": "Get a list of all enrolled students and groups.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_scores",
            "description": "Get score distribution (4 buckets) for a specific lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "The ID of the lab, e.g. 'lab-03'",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_pass_rates",
            "description": "Get per-task average scores and attempt counts for a specific lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "The ID of the lab, e.g. 'lab-03'",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_timeline",
            "description": "Get the number of submissions per day for a specific lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "The ID of the lab, e.g. 'lab-03'",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_groups",
            "description": "Get per-group average scores and student counts for a specific lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "The ID of the lab, e.g. 'lab-03'",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_learners",
            "description": "Get top N learners by score for a specific lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "The ID of the lab, e.g. 'lab-03'",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "The number of top learners to return. Default is 10.",
                    },
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_completion_rate",
            "description": "Get completion rate percentage for a specific lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "The ID of the lab, e.g. 'lab-03'",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "trigger_sync",
            "description": "Refresh data from autochecker pipeline.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]


class IntentRouter:
    def __init__(self, lms_client: LMSClient):
        self.lms_client = lms_client
        self.llm_url = f"{settings.llm_api_base_url}/chat/completions"
        self.llm_model = settings.llm_api_model
        self.api_key = settings.llm_api_key

    async def _execute_tool(self, name: str, arguments: dict) -> Any:
        try:
            if name == "get_items":
                return await self.lms_client.get_items()
            elif name == "get_learners":
                return await self.lms_client.get_learners()
            elif name == "get_scores":
                return await self.lms_client.get_scores_distribution(
                    arguments.get("lab", "")
                )
            elif name == "get_pass_rates":
                return await self.lms_client.get_pass_rates(arguments.get("lab", ""))
            elif name == "get_timeline":
                return await self.lms_client.get_timeline(arguments.get("lab", ""))
            elif name == "get_groups":
                return await self.lms_client.get_groups(arguments.get("lab", ""))
            elif name == "get_top_learners":
                return await self.lms_client.get_top_learners(
                    arguments.get("lab", ""), limit=arguments.get("limit", 10)
                )
            elif name == "get_completion_rate":
                return await self.lms_client.get_completion_rate(
                    arguments.get("lab", "")
                )
            elif name == "trigger_sync":
                return await self.lms_client.trigger_sync()
            else:
                return {"error": f"Unknown tool: {name}"}
        except httpx.HTTPError as e:
            return {"error": f"Backend API error: {e}"}
        except Exception as e:
            return {"error": str(e)}

    async def route(self, user_message: str) -> str:
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant for a Learning Management System (LMS). Use the provided tools to answer user questions about labs, learners, scores, and statistics. Provide clear, concise answers. If a tool fails, inform the user. When asked to compare items (like labs or groups), you must use the appropriate tools to fetch data for all items needed before giving your final answer. Do not describe your intermediate steps or calculations to the user; just fetch the necessary data immediately using the tools and then provide the final answer.",
            },
            {"role": "user", "content": user_message},
        ]

        async with httpx.AsyncClient(timeout=30) as client:
            while True:
                payload = {
                    "model": self.llm_model,
                    "messages": messages,
                    "tools": TOOLS,
                }
                headers = (
                    {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
                )
                try:
                    response = await client.post(
                        self.llm_url, json=payload, headers=headers
                    )
                    if response.status_code != 200:
                        return f"Error communicating with LLM: {response.text}"
                except Exception as e:
                    return f"Error communicating with LLM: {str(e)}"

                res_data = response.json()
                choice = res_data["choices"][0]
                message = choice["message"]

                if message.get("tool_calls"):
                    # print(f"[summary] Feeding {len(message['tool_calls'])} tool results back to LLM", file=sys.stderr)
                    messages.append(
                        {
                            "role": "assistant",
                            "content": message.get("content") or "",
                            "tool_calls": message["tool_calls"],
                        }
                    )

                    for tool_call in message["tool_calls"]:
                        fn_name = tool_call["function"]["name"]
                        args_str = tool_call["function"]["arguments"] or "{}"

                        if not fn_name:
                            result_str = json.dumps(
                                {"error": "No function name provided"}
                            )
                            messages.append(
                                {
                                    "role": "tool",
                                    "tool_call_id": tool_call["id"],
                                    "name": "unknown",
                                    "content": result_str,
                                }
                            )
                            continue

                        try:
                            args = json.loads(args_str)
                        except json.JSONDecodeError:
                            args = {}

                        print(
                            f"[tool] LLM called: {fn_name}({args_str})", file=sys.stderr
                        )
                        result = await self._execute_tool(fn_name, args)

                        result_str = json.dumps(result)
                        if isinstance(result, list):
                            print(
                                f"[tool] Result: {len(result)} items", file=sys.stderr
                            )
                        else:
                            print(
                                f"[tool] Result: {result_str[:100]}...", file=sys.stderr
                            )

                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": tool_call["id"],
                                "name": fn_name,
                                "content": result_str,
                            }
                        )
                else:
                    return message.get(
                        "content", "I am not sure how to respond to that."
                    )
