import json
import anthropic
from config import Config

MODEL = "claude-sonnet-4-6"


class ClaudeClient:
    def __init__(self, config: Config):
        self._client = anthropic.Anthropic(api_key=config.anthropic_api_key)

    def analyze_tweets(self, username: str, tweets: list[dict]) -> dict:
        tweets_text = json.dumps(tweets, ensure_ascii=False, indent=2)
        prompt = f"""以下は @{username} のツイートデータです。このアカウントの特徴を分析し、
必ず以下のフィールドを含むJSONのみを返してください。説明文や前置きは不要です。

ツイートデータ:
{tweets_text}

返すJSONフォーマット:
{{
  "username": "@{username}",
  "analyzed_tweet_count": <整数>,
  "posting_frequency": "<投稿頻度の説明>",
  "common_keywords": ["キーワード1", "キーワード2", ...],
  "common_hashtags": ["#タグ1", "#タグ2", ...],
  "tone": "<フォーマル/カジュアル/ユーモア/専門的/etc>",
  "style_characteristics": ["特徴1", "特徴2", ...],
  "high_engagement_patterns": ["高エンゲージメントパターン1", ...],
  "avg_like_count": <平均いいね数 float>,
  "avg_retweet_count": <平均RT数 float>,
  "summary": "<総合的な特徴まとめ（200字以内）>"
}}"""

        message = self._client.messages.create(
            model=MODEL,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = message.content[0].text.strip()
        # Strip markdown code blocks if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw)

    def generate_tweets(
        self,
        theme: str,
        tone: str,
        strategy: str = "similar",
        analysis: dict | None = None,
    ) -> list[str]:
        analysis_section = ""
        if analysis:
            analysis_section = f"""
参考にする競合アカウント分析:
- アカウント: {analysis.get('username', '')}
- トーン: {analysis.get('tone', '')}
- スタイル特徴: {', '.join(analysis.get('style_characteristics', []))}
- よく使うキーワード: {', '.join(analysis.get('common_keywords', [])[:5])}
- 高エンゲージメントパターン: {', '.join(analysis.get('high_engagement_patterns', []))}
- 総評: {analysis.get('summary', '')}
"""
            if strategy == "similar":
                strategy_instruction = "上記の競合アカウントのスタイル・文体・表現を参考にして、似たスタイルでツイートを生成してください。"
            else:
                strategy_instruction = "上記の競合アカウントとは差別化した、独自のアングル・視点・表現でツイートを生成してください。"
        else:
            strategy_instruction = "独自のスタイルでツイートを生成してください。"

        prompt = f"""以下の条件でツイートを3案生成してください。
各ツイートは140文字以内で、番号付きリスト（1. 2. 3.）で返してください。
ツイート本文のみを返し、説明や前置きは不要です。
{analysis_section}
テーマ: {theme}
トーン: {tone}
戦略: {strategy_instruction}"""

        message = self._client.messages.create(
            model=MODEL,
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = message.content[0].text.strip()
        tweets = []
        for line in raw.splitlines():
            line = line.strip()
            if line and line[0].isdigit() and ". " in line:
                _, text = line.split(". ", 1)
                tweets.append(text.strip())
        return tweets
