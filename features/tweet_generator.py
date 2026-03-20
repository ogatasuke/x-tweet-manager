from services.x_client import XClient, RateLimitError
from services.claude_client import ClaudeClient
from services import analysis_store
from cli import display, menus
from rich.progress import Progress, SpinnerColumn, TextColumn

try:
    import pyperclip
    _CLIPBOARD_AVAILABLE = True
except ImportError:
    _CLIPBOARD_AVAILABLE = False


def run(x_client: XClient, claude_client: ClaudeClient):
    display.console.print("\n[bold cyan]=== ツイート生成・投稿 ===[/bold cyan]")

    theme = menus.prompt_theme()
    tone = menus.prompt_tone()
    strategy = menus.prompt_strategy()
    hook_structure = menus.prompt_hook_structure()

    analyses = analysis_store.list_analyses()
    analysis_data = None
    if analyses:
        display.print_analyses_list(analyses)
        selected = menus.prompt_select_analysis(analyses)
        if selected:
            full = analysis_store.load(selected["username"].lstrip("@"))
            analysis_data = full

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task("Claude でツイートを生成中...", total=None)
        try:
            tweets = claude_client.generate_tweets(
                theme=theme,
                tone=tone,
                strategy=strategy,
                analysis=analysis_data,
                hook_structure=hook_structure,
            )
        except Exception as e:
            display.print_error(f"生成エラー: {e}")
            return

    if not tweets:
        display.print_warning("ツイートが生成されませんでした。")
        return

    display.print_tweets(tweets, hook_structure=hook_structure)

    for i, tweet in enumerate(tweets, 1):
        action = menus.prompt_tweet_action(tweet, i)
        if action == "post":
            if not menus.confirm_post(tweet):
                display.print_info("投稿をキャンセルしました。")
                continue
            try:
                tweet_id = x_client.post_tweet(tweet)
                display.print_success(f"投稿しました！ ID: {tweet_id}")
            except RateLimitError as e:
                display.print_error(str(e))
            except PermissionError as e:
                display.print_error(str(e))
            except Exception as e:
                display.print_error(f"投稿エラー: {e}")
        elif action == "copy":
            if _CLIPBOARD_AVAILABLE:
                pyperclip.copy(tweet)
                display.print_success("クリップボードにコピーしました。")
            else:
                display.print_warning("pyperclip が利用できません。手動でコピーしてください。")
                display.console.print(f"\n  {tweet}\n")
        else:
            display.print_info("スキップしました。")
