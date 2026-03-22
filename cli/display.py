from typing import List, Tuple
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()


def print_header():
    console.print("\n[bold cyan]X ツイートマネージャー[/bold cyan]  [dim]競合分析 & ツイート自動生成[/dim]\n")


def print_success(msg: str):
    console.print(f"[green]✓[/green] {msg}")


def print_error(msg: str):
    console.print(f"[red]✗[/red] {msg}")


def print_warning(msg: str):
    console.print(f"[yellow]⚠[/yellow] {msg}")


def print_info(msg: str):
    console.print(f"[dim]{msg}[/dim]")


def print_analysis(analysis: dict):
    username = analysis.get("username", "")
    console.print(f"\n[bold cyan]{username}[/bold cyan] の分析結果\n")

    rows = [
        ("投稿頻度", analysis.get("posting_frequency", "-")),
        ("トーン", analysis.get("tone", "-")),
        ("キーワード", ", ".join(analysis.get("common_keywords", []))),
        ("ハッシュタグ", ", ".join(analysis.get("common_hashtags", []))),
        ("スタイル特徴", "  ".join(f"・{s}" for s in analysis.get("style_characteristics", []))),
        ("高エンゲージ", "  ".join(f"・{p}" for p in analysis.get("high_engagement_patterns", []))),
        ("平均いいね/RT", f"{analysis.get('avg_like_count', '-')} / {analysis.get('avg_retweet_count', '-')}"),
    ]
    for key, val in rows:
        if val and val not in ("-", ""):
            console.print(f"  [dim]{key}[/dim]  {val}")

    if analysis.get("summary"):
        console.print(f"\n  [dim]総評[/dim]  {analysis['summary']}\n")


def print_tweets(tweets: List[str]):
    console.print()
    for i, tweet in enumerate(tweets, 1):
        char_count = len(tweet)
        color = "green" if char_count <= 140 else "red"
        console.print(
            Panel(
                tweet + f"\n\n[dim]{char_count}/140 文字[/dim]",
                title=f"[bold]案 {i}[/bold]",
                border_style=color,
                padding=(0, 1),
            )
        )


def print_analyses_list(analyses: List[dict]):
    if not analyses:
        print_info("保存済みの分析データがありません。")
        return
    console.print()
    for i, a in enumerate(analyses, 1):
        saved = a.get("saved_at", "")[:10]
        console.print(f"  [yellow]{i}[/yellow]  [cyan]{a.get('username', '')}[/cyan]  [dim]{saved}[/dim]")
        if a.get("summary"):
            console.print(f"     [dim]{a['summary'][:60]}{'…' if len(a.get('summary',''))>60 else ''}[/dim]")
    console.print()
