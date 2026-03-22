from typing import Optional, List
from rich.prompt import Prompt, Confirm
from cli.display import console

TONE_OPTIONS = ["カジュアル", "フォーマル", "ユーモア", "専門的", "情熱的", "共感的"]
STRATEGY_OPTIONS = [("1", "similar", "競合を模倣"), ("2", "differentiated", "差別化")]


def prompt_main_choice() -> str:
    console.print(
        "\n  [bold yellow]1[/bold yellow]  競合アカウントを分析"
        "\n  [bold yellow]2[/bold yellow]  ツイートを生成"
        "\n  [bold yellow]3[/bold yellow]  保存済み分析を見る"
        "\n  [bold yellow]q[/bold yellow]  終了\n"
    )
    return Prompt.ask("[bold]選択[/bold]", choices=["1", "2", "3", "q"])


def prompt_username() -> str:
    username = Prompt.ask("競合アカウント（@ユーザー名）")
    return username.lstrip("@")


def prompt_theme() -> str:
    return Prompt.ask("ツイートのテーマ")


def prompt_tone() -> str:
    console.print("\nトーン: " + "  ".join(
        f"[yellow]{i}[/yellow] {t}" for i, t in enumerate(TONE_OPTIONS, 1)
    ))
    val = Prompt.ask("選択", default="1")
    try:
        idx = int(val) - 1
        if 0 <= idx < len(TONE_OPTIONS):
            return TONE_OPTIONS[idx]
    except ValueError:
        pass
    return Prompt.ask("トーンを入力")


def prompt_strategy() -> str:
    console.print("\n戦略:  [yellow]1[/yellow] 競合を模倣  [yellow]2[/yellow] 差別化")
    val = Prompt.ask("選択", choices=["1", "2"], default="1")
    return "similar" if val == "1" else "differentiated"


def prompt_select_analysis(analyses: List[dict]) -> Optional[dict]:
    if not analyses:
        return None
    use = Confirm.ask("保存済み分析を参照する？", default=True)
    if not use:
        return None
    if len(analyses) == 1:
        console.print(f"  → [cyan]{analyses[0]['username']}[/cyan] を使用")
        return analyses[0]
    for i, a in enumerate(analyses, 1):
        console.print(f"  [yellow]{i}[/yellow]  {a['username']}")
    val = Prompt.ask("選択", choices=[str(i) for i in range(1, len(analyses) + 1)], default="1")
    return analyses[int(val) - 1]


def prompt_tweet_select(count: int) -> str:
    """Return '1'-'count' to copy, or 'n' to skip."""
    choices = [str(i) for i in range(1, count + 1)] + ["n"]
    return Prompt.ask(
        f"コピーする案を選択 ([yellow]1[/yellow]–[yellow]{count}[/yellow] / [yellow]n[/yellow] でスキップ)",
        choices=choices,
        default="1",
    )


def confirm_post(tweet: str) -> bool:
    return Confirm.ask(f"投稿しますか？（月500件上限）\n  {tweet}", default=False)
