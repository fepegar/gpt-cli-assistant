import os
from rich import print
from typing import List

import openai
import typer


app = typer.Typer()


@app.command()
def main(
    args: List[str] = typer.Argument(
        None,
        help="Query to ask GPT-4.",
        metavar="QUERY",
    ),
) -> None:
    query = " ".join(args)

    openai.api_key = os.getenv("OPENAI_API_KEY")

    prompt = (
        f"Write a cool zsh command (no explanations) to {query}:"
        "\n\n```zsh\n#!/bin/zsh\n\n"
    )

    messages = [
        {"role": "system", "content": "You are a helpful assistant, expert in zsh."},
        {"role": "user", "content": prompt},
    ]

    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
    )

    answer: str = completion.choices[0].message.content
    answer = answer.strip('`').strip('\n')
    print(answer)


if __name__ == "__main__":
    app.run()
