import httpx
from decouple import config

class TelegramBot:
    def __init__(self, token: str):
        self.client = httpx.AsyncClient()
        self.token = token

    async def is_user_chat(self, chat_id: int, user_id: int):
        data = {
            "chat_id": chat_id,
            "user_id": user_id,
        }
        resp = await self.client.get(f'https://api.telegram.org/bot{self.token}/getChatMember', params=data)
        resp_js = resp.json()
        if resp_js['ok']:
            return resp_js['result']['status'] != 'left'

        raise Exception('Error getting chat member')

telegram_bot = TelegramBot(config('TELEGRAM_TOKEN'))
