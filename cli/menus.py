from typing import Optional, List
from rich.prompt import Prompt, Confirm
from cli.display import console, print_menu

MAIN_MENU = [
    ("1", "競合アカウント分析"),
    ("2", "ツイート生成・投稿"),
    ("3", "保存済み分析一覧"),
    ("q", "終了"),
]

TONE_OPTIONS = ["カジュアル", "フォーマル", "ユーモア", "専門的", "情熱的", "共感的"]
STRATEGY_OPTIONS = [("1", "similar", "競合を模倣"), ("2", "differentiated", "差別化")]


def prompt_main_choice() -> str:
    print_menu(MAIN_MENU)
    return Prompt.ask("[bold]選択してください[/bold]", choices=["1", "2", "3", "q"])


def prompt_username() -> str:
    username = Prompt.ask("競合アカウントの @ユーザー名 を入力")
    return username.lstrip("@")


def prompt_tweet_count() -> int:
    val = Prompt.ask("取得するツイート数", default="20")
    try:
        n = int(val)
        return max(5, min(100, n))
    except ValueError:
        return 20


def prompt_theme() -> str:
    return Prompt.ask("ツイートのテーマを入力（例: AI技術の最新動向）")


def prompt_tone() -> str:
    console.print("\nトーンを選択:")
    for i, t in enumerate(TONE_OPTIONS, 1):
        console.print(f"  [yellow]{i}[/yellow]  {t}")
    console.print(f"  [yellow]{len(TONE_OPTIONS)+1}[/yellow]  カスタム入力")
    val = Prompt.ask("番号を選択", default="1")
    try:
        idx = int(val) - 1
        if 0 <= idx < len(TONE_OPTIONS):
            return TONE_OPTIONS[idx]
    except ValueError:
        pass
    return Prompt.ask("トーンを入力")


def prompt_strategy() -> str:
    console.print("\n生成戦略を選択:")
    for key, _, label in STRATEGY_OPTIONS:
        console.print(f"  [yellow]{key}[/yellow]  {label}")
    val = Prompt.ask("番号を選択", choices=["1", "2"], default="1")
    for key, strategy, _ in STRATEGY_OPTIONS:
        if val == key:
            return strategy
    return "similar"


def prompt_hook_structure() -> bool:
    console.print(
        "\n[bold]ツイート構成:[/bold]"
        " [dim]フック → 興味付け → 強化要素[/dim] の3要素構成を使いますか？"
    )
    return Confirm.ask("3要素構成を使用する", default=True)


def prompt_select_analysis(analyses: List[dict]) -> Optional[dict]:
    if not analyses:
        return None
    use = Confirm.ask("保存済み競合分析を参照しますか？", default=True)
    if not use:
        return None
    if len(analyses) == 1:
        return analyses[0]
    val = Prompt.ask(
        "番号を選択",
        choices=[str(i) for i in range(1, len(analyses) + 1)],
        default="1",
    )
    return analyses[int(val) - 1]


def prompt_tweet_action(tweet: str, index: int) -> str:
    console.print(f"\n案 {index}:")
    console.print(f"  {tweet}")
    return Prompt.ask(
        "操作",
        choices=["post", "copy", "skip"],
        default="copy",
        show_choices=True,
    )


def confirm_post(tweet: str) -> bool:
    return Confirm.ask(
        f"以下のツイートを投稿しますか？（月500件上限に注意）\n  {tweet}", default=False
    )
