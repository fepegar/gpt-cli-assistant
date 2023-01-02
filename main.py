from dotenv import load_dotenv
import os
import openai
import subprocess
import json
import argparse


class Styles:
    bold = "\u001b[1m"
    underline = "\u001b[4m"
    inverted = "\u001b[7m"
    reset = "\u001b[0m"
    green = "\u001b[38;5;121m"
    blue = "\u001b[38;5;117m"
    red = "\u001b[38;5;198m"
    yellow = "\u001b[38;5;228m"
    white = "\u001b[38;5;255m"
    black = "\u001b[38;5;234m"
    bg_green = "\u001b[48;5;121m"
    bg_blue = "\u001b[48;5;117m"
    bg_red = "\u001b[48;5;198m"
    bg_yellow = "\u001b[48;5;228m"
    bg_white = "\u001b[48;5;255m"
    bg_black = "\u001b[48;5;234m"


def styled(txt: str, style: str = ''):
    return style + txt + Styles.reset


if __name__ == "__main__":

    max_history = 300

    load_dotenv()

    parser = argparse.ArgumentParser()

    parser.add_argument('terminal_command_request')

    parser.add_argument(
        "-e",
        "--execute",
        help="DANGER! This will execute the command immediately. ",
        action='store_true'
    )
    parser.add_argument(
        "-s",
        "--set_key",
        help="Reset API key",
        type=str,
        required=False,
    )

    args = parser.parse_args()

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key or args.set_key:
        if args.set_key is not None:
            api_key = args.set_key
        else:
            api_key = input("Input your API key to be saved to '.env':")

        with open('.env', 'w') as f:
            f.write(f'OPENAI_API_KEY = "{api_key}"')

    openai.api_key = api_key

    # Get the first command line argument
    terminal_command_request = args.terminal_command_request

    try:
        with open('request_history.json', mode="r") as f:
            history = json.loads(f.read())
    except FileNotFoundError:
        history: dict = {}

    if terminal_command_request in history.keys():
        answer = history[terminal_command_request]
    else:

        response = openai.Completion.create(
            model="code-cushman-001",
            prompt="Generate a bash script to " + terminal_command_request + "\n```bash\n#!/bin/bash",
            temperature=0,
            max_tokens=54,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=["```"]
        )

        answer = response["choices"][0]['text'].strip()

        # update cache
        history.update({terminal_command_request: answer})
        if len(history.keys()) > max_history:
            history = {i: history[i] for i in history if list(history.keys()).index(i) < max_history}

        with open('request_history.json', mode="w") as f:
            f.write(json.dumps(history))

    if args.execute:
        print(styled("> ", Styles.bg_red) + styled(answer, Styles.blue + Styles.inverted))

        # shell_output = os.system(answer)
        shell_output = subprocess.run(answer, stdout=subprocess.PIPE, shell=True)

        print(shell_output.stdout.decode("utf-8"))
    else:
        print(styled(answer, Styles.blue))
