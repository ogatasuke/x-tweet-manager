from services.x_client import XClient, RateLimitError
from services.claude_client import ClaudeClient
from services import analysis_store
from cli import display, menus
from rich.progress import Progress, SpinnerColumn, TextColumn


def run(x_client: XClient, claude_client: ClaudeClient):
    display.console.print("\n[bold cyan]=== 競合アカウント分析 ===[/bold cyan]")
    username = menus.prompt_username()
    cached = analysis_store.load(username)

    if cached:
        saved_at = cached.get("saved_at", "")[:19].replace("T", " ")
        display.print_info(f"キャッシュあり（{saved_at}）")
        from rich.prompt import Confirm
        use_cache = Confirm.ask("キャッシュを使用しますか？（Noで再取得）", default=True)
        if use_cache:
            display.print_analysis(cached)
            return cached

    tweet_count = menus.prompt_tweet_count()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task(f"@{username} のツイートを取得中...", total=None)
        try:
            tweets = x_client.get_user_tweets(username, max_results=tweet_count)
        except RateLimitError as e:
            progress.stop()
            display.print_warning(str(e))
            if cached:
                display.print_info("キャッシュデータを使用します。")
                display.print_analysis(cached)
                return cached
            display.print_error("キャッシュもなく、データを取得できませんでした。")
            return None
        except PermissionError as e:
            progress.stop()
            display.print_warning(str(e))
            if cached:
                display.print_info("キャッシュデータを使用します。")
                display.print_analysis(cached)
                return cached
            display.print_error("キャッシュもなく、データを取得できませんでした。")
            return None

        if not tweets:
            progress.stop()
            display.print_warning(f"@{username} のツイートが見つかりませんでした。")
            return None

        progress.update(task, description=f"Claude で分析中（{len(tweets)}件）...")
        try:
            analysis = claude_client.analyze_tweets(username, tweets)
        except Exception as e:
            progress.stop()
            display.print_error(f"Claude 分析エラー: {e}")
            return None

    path = analysis_store.save(username, analysis)
    display.print_success(f"分析結果を保存しました: {path}")
    display.print_analysis(analysis)
    return analysis
