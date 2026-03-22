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
    theme = menus.prompt_theme()
    tone = menus.prompt_tone()
    strategy = menus.prompt_strategy()

    analyses = analysis_store.list_analyses()
    analysis_data = None
    if analyses:
        display.print_analyses_list(analyses)
        selected = menus.prompt_select_analysis(analyses)
        if selected:
            analysis_data = analysis_store.load(selected["username"].lstrip("@"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task("ツイートを生成中...", total=None)
        try:
            tweets = claude_client.generate_tweets(
                theme=theme,
                tone=tone,
                strategy=strategy,
                analysis=analysis_data,
                hook_structure=True,
            )
        except Exception as e:
            display.print_error(f"生成エラー: {e}")
            return

    if not tweets:
        display.print_warning("ツイートが生成されませんでした。")
        return

    display.print_tweets(tweets)

    choice = menus.prompt_tweet_select(len(tweets))
    if choice == "n":
        display.print_info("スキップしました。")
        return

    tweet = tweets[int(choice) - 1]

    if _CLIPBOARD_AVAILABLE:
        pyperclip.copy(tweet)
        display.print_success("クリップボードにコピーしました。")
    else:
        display.print_warning("pyperclip が利用できません。")
        display.console.print(f"\n  {tweet}\n")

    if menus.confirm_post(tweet):
        try:
            tweet_id = x_client.post_tweet(tweet)
            display.print_success(f"投稿しました！ ID: {tweet_id}")
        except RateLimitError as e:
            display.print_error(str(e))
        except PermissionError as e:
            display.print_error(str(e))
        except Exception as e:
            display.print_error(f"投稿エラー: {e}")
