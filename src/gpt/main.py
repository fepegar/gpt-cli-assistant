import os
import pwd
import subprocess
from pathlib import Path
from rich import print
from typing import List

import openai
import typer

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


app = typer.Typer()


def get_shell_path() -> Path:
    return Path(pwd.getpwuid(os.getuid()).pw_shell)


@app.command()
def main(
    args: List[str] = typer.Argument(
        None,
        help="Query to ask GPT-4.",
        metavar="QUERY",
    ),
) -> None:
    """Ask GPT-4 for a shell command.

    Example:

        $ ai count the number of lines in all Python files in the current directory
    """
    query = " ".join(args)

    openai.api_key = os.getenv("OPENAI_API_KEY")

    shell_path = get_shell_path()
    shell_name = shell_path.name

    prompt = (
        f"Write a {shell_name} command (no explanations) to {query}:"
        f"\n\n```{shell_name}\n#!{shell_path}\n\n"
    )

    messages = [
        {"role": "system", "content": "You are a helpful assistant, expert in shell programming."},
        {"role": "user", "content": prompt},
    ]

    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
    )

    answer: str = completion.choices[0].message.content
    answer = answer.strip('`').strip()
    print(answer)

    print(r'Run the command? \[y/n]', end=' ')
    while True:
        key = typer.getchar()
        if key == 'y':
            print(f'\n$ {answer}')
            result = subprocess.run(answer, capture_output=True, shell=True, text=True)
            print(result.stdout.rstrip())
            break
        elif key == 'n':
            break


if __name__ == "__main__":
    app.run()
