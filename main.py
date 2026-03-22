#!/usr/bin/env python3
import sys
from config import load_config
from services.x_client import XClient
from services.claude_client import ClaudeClient
from services import analysis_store
from cli import display, menus
from features import competitor_analysis, tweet_generator


def main():
    display.print_header()

    try:
        config = load_config()
    except ValueError as e:
        display.print_error(str(e))
        sys.exit(1)

    x_client = XClient(config)
    claude_client = ClaudeClient(config)

    while True:
        try:
            choice = menus.prompt_main_choice()
        except KeyboardInterrupt:
            display.console.print()
            break

        if choice == "q":
            break
        elif choice == "1":
            try:
                competitor_analysis.run(x_client, claude_client)
            except KeyboardInterrupt:
                display.print_info("キャンセル")
        elif choice == "2":
            try:
                tweet_generator.run(x_client, claude_client)
            except KeyboardInterrupt:
                display.print_info("キャンセル")
        elif choice == "3":
            analyses = analysis_store.list_analyses()
            display.print_analyses_list(analyses)
            if analyses:
                from rich.prompt import Prompt
                val = Prompt.ask(
                    "詳細を見る（番号 / Enter でスキップ）",
                    default="",
                )
                if val.isdigit() and 1 <= int(val) <= len(analyses):
                    full = analysis_store.load(analyses[int(val) - 1]["username"].lstrip("@"))
                    if full:
                        display.print_analysis(full)


if __name__ == "__main__":
    main()
