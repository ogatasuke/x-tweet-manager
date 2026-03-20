import tweepy
from config import Config


class RateLimitError(Exception):
    pass


class XClient:
    def __init__(self, config: Config):
        self._config = config
        # App-only auth for read operations
        self._app_client = tweepy.Client(
            bearer_token=config.x_bearer_token,
            wait_on_rate_limit=False,
        )
        # OAuth 1.0a for write operations
        self._user_client = tweepy.Client(
            consumer_key=config.x_api_key,
            consumer_secret=config.x_api_secret,
            access_token=config.x_access_token,
            access_token_secret=config.x_access_token_secret,
            wait_on_rate_limit=False,
        )

    def get_user_id(self, username: str) -> str:
        try:
            resp = self._app_client.get_user(username=username)
        except tweepy.TooManyRequests:
            raise RateLimitError(
                f"レート制限に達しました。しばらく待ってから再試行してください。"
            )
        except tweepy.Forbidden:
            raise PermissionError(
                "このAPIエンドポイントへのアクセス権限がありません。"
                "Basic tier ($100/月) が必要な場合があります。"
            )
        if not resp.data:
            raise ValueError(f"ユーザー @{username} が見つかりませんでした。")
        return str(resp.data.id)

    def get_user_tweets(self, username: str, max_results: int = 20) -> list[dict]:
        try:
            user_id = self.get_user_id(username)
            resp = self._app_client.get_users_tweets(
                id=user_id,
                max_results=min(max_results, 100),
                tweet_fields=["created_at", "public_metrics", "text"],
                exclude=["retweets", "replies"],
            )
        except tweepy.TooManyRequests:
            raise RateLimitError(
                "レート制限に達しました。しばらく待ってから再試行してください。"
            )
        except tweepy.Forbidden:
            raise PermissionError(
                "タイムライン読み取りには Basic tier ($100/月) が必要です。\n"
                "キャッシュ済みの分析データを使用します。"
            )
        if not resp.data:
            return []
        tweets = []
        for t in resp.data:
            metrics = t.public_metrics or {}
            tweets.append(
                {
                    "id": str(t.id),
                    "text": t.text,
                    "created_at": str(t.created_at),
                    "like_count": metrics.get("like_count", 0),
                    "retweet_count": metrics.get("retweet_count", 0),
                    "reply_count": metrics.get("reply_count", 0),
                }
            )
        return tweets

    def post_tweet(self, text: str) -> str:
        try:
            resp = self._user_client.create_tweet(text=text)
        except tweepy.TooManyRequests:
            raise RateLimitError(
                "投稿レート制限に達しました（月500件上限）。後で再試行してください。"
            )
        except tweepy.Forbidden as e:
            raise PermissionError(f"投稿権限エラー: {e}")
        return str(resp.data["id"])
