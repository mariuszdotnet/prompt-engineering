import argparse
import os
import tomllib
from pathlib import Path
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

__all__ = ["get_chat_completion"]

# Authenticate
client = AzureOpenAI(
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), 
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
    api_version="2024-02-01"
)

# Load settings file
settings_path = Path("settings.toml")
with settings_path.open("rb") as settings_file:
    SETTINGS = tomllib.load(settings_file)


def parse_args() -> argparse.Namespace:
    """Parse command-line input."""
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", type=Path, help="Path to the input file")
    return parser.parse_args()


def main(args: argparse.Namespace) -> None:
    file_content = args.file_path.read_text("utf-8")
    print(get_chat_completion(file_content))


def get_chat_completion(content: str) -> str:
    """Send a request to the /chat/completions endpoint."""
    response = client.chat.completions.create(model=SETTINGS["general"]["model"],
                                         temperature=SETTINGS["general"]["temperature"],
                                         messages=_assemble_chat_messages(content),
                                         seed=12345)
    return response.choices[0].message.content


def _assemble_chat_messages(content: str) -> list[dict]:
    """Combine all messages into a well-formatted list of dicts."""
    messages = [
        {"role": "system", "content": SETTINGS["prompts"]["role_prompt"]},
        {"role": "user", "content": SETTINGS["prompts"]["negative_example"]},
        {
            "role": "system",
            "content": SETTINGS["prompts"]["negative_reasoning"],
        },
        {
            "role": "assistant",
            "content": SETTINGS["prompts"]["negative_output"],
        },
        {"role": "user", "content": SETTINGS["prompts"]["positive_example"]},
        {
            "role": "system",
            "content": SETTINGS["prompts"]["positive_reasoning"],
        },
        {
            "role": "assistant",
            "content": SETTINGS["prompts"]["positive_output"],
        },
        {"role": "user", "content": f">>>>>\n{content}\n<<<<<"},
        {"role": "user", "content": SETTINGS["prompts"]["instruction_prompt"]},
    ]
    return messages


if __name__ == "__main__":
    main(parse_args())
