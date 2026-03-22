from services.x_client import XClient, RateLimitError
from services.claude_client import ClaudeClient
from services import analysis_store
from cli import display, menus
from rich.progress import Progress, SpinnerColumn, TextColumn


def run(x_client: XClient, claude_client: ClaudeClient):
    username = menus.prompt_username()
    cached = analysis_store.load(username)

    if cached:
        saved_at = cached.get("saved_at", "")[:10]
        display.print_info(f"キャッシュ（{saved_at}）を使用します。再取得する場合は一度終了してキャッシュを削除してください。")
        display.print_analysis(cached)
        return cached

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task(f"@{username} のツイートを取得中...", total=None)
        try:
            tweets = x_client.get_user_tweets(username, max_results=20)
        except (RateLimitError, PermissionError) as e:
            progress.stop()
            display.print_warning(str(e))
            display.print_error("データを取得できませんでした。")
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
            display.print_error(f"分析エラー: {e}")
            return None

    analysis_store.save(username, analysis)
    display.print_success("分析完了・保存しました")
    display.print_analysis(analysis)
    return analysis
