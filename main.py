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
            display.console.print("\n")
            display.print_info("終了します。")
            break

        if choice == "q":
            display.print_info("終了します。")
            break
        elif choice == "1":
            try:
                competitor_analysis.run(x_client, claude_client)
            except KeyboardInterrupt:
                display.print_info("キャンセルしました。")
        elif choice == "2":
            try:
                tweet_generator.run(x_client, claude_client)
            except KeyboardInterrupt:
                display.print_info("キャンセルしました。")
        elif choice == "3":
            analyses = analysis_store.list_analyses()
            display.print_analyses_list(analyses)
            if analyses:
                from rich.prompt import Confirm
                if Confirm.ask("詳細を表示しますか？", default=False):
                    from rich.prompt import Prompt
                    val = Prompt.ask(
                        "番号を選択",
                        choices=[str(i) for i in range(1, len(analyses) + 1)],
                    )
                    selected = analyses[int(val) - 1]
                    full = analysis_store.load(selected["username"].lstrip("@"))
                    if full:
                        display.print_analysis(full)


if __name__ == "__main__":
    main()
