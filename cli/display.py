from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()


def print_header():
    console.print(
        Panel.fit(
            "[bold cyan]X ツイートマネージャー[/bold cyan]\n"
            "[dim]競合分析 & ツイート自動生成[/dim]",
            box=box.DOUBLE,
        )
    )


def print_menu(items: list[tuple[str, str]]):
    console.print()
    for key, label in items:
        console.print(f"  [bold yellow]{key}[/bold yellow]  {label}")
    console.print()


def print_success(msg: str):
    console.print(f"[bold green]✓[/bold green] {msg}")


def print_error(msg: str):
    console.print(f"[bold red]✗[/bold red] {msg}")


def print_warning(msg: str):
    console.print(f"[bold yellow]⚠[/bold yellow] {msg}")


def print_info(msg: str):
    console.print(f"[cyan]ℹ[/cyan] {msg}")


def print_analysis(analysis: dict):
    console.print()
    console.print(
        Panel(
            f"[bold]{analysis.get('username', '')}[/bold] の分析結果",
            style="cyan",
        )
    )
    table = Table(box=box.SIMPLE, show_header=False)
    table.add_column("項目", style="bold")
    table.add_column("内容")

    table.add_row("ツイート数", str(analysis.get("analyzed_tweet_count", "-")))
    table.add_row("投稿頻度", analysis.get("posting_frequency", "-"))
    table.add_row("トーン", analysis.get("tone", "-"))
    table.add_row(
        "キーワード", ", ".join(analysis.get("common_keywords", []))
    )
    table.add_row(
        "ハッシュタグ", ", ".join(analysis.get("common_hashtags", []))
    )
    table.add_row(
        "スタイル特徴", "\n".join(f"• {s}" for s in analysis.get("style_characteristics", []))
    )
    table.add_row(
        "高エンゲージメント",
        "\n".join(f"• {p}" for p in analysis.get("high_engagement_patterns", [])),
    )
    table.add_row("平均いいね", str(analysis.get("avg_like_count", "-")))
    table.add_row("平均RT", str(analysis.get("avg_retweet_count", "-")))
    console.print(table)
    console.print(
        Panel(analysis.get("summary", ""), title="総評", border_style="dim")
    )


def print_tweets(tweets: list[str]):
    console.print()
    for i, tweet in enumerate(tweets, 1):
        char_count = len(tweet)
        color = "green" if char_count <= 140 else "red"
        console.print(
            Panel(
                tweet + f"\n\n[dim]{char_count}/140 文字[/dim]",
                title=f"[bold]案 {i}[/bold]",
                border_style=color,
            )
        )


def print_analyses_list(analyses: list[dict]):
    if not analyses:
        print_info("保存済みの分析データがありません。")
        return
    table = Table(title="保存済み分析一覧", box=box.ROUNDED)
    table.add_column("番号", style="bold yellow", width=6)
    table.add_column("アカウント", style="cyan")
    table.add_column("保存日時")
    table.add_column("概要")
    for i, a in enumerate(analyses, 1):
        saved = a.get("saved_at", "")[:19].replace("T", " ")
        summary = a.get("summary", "")[:40] + ("…" if len(a.get("summary", "")) > 40 else "")
        table.add_row(str(i), a.get("username", ""), saved, summary)
    console.print(table)
