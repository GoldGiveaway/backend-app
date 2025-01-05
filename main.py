import json
import hashlib
import hmac
import hashlib
from urllib.parse import unquote, parse_qs
from fastapi import FastAPI
from pydantic import BaseModel
import grpc
import giveaway_pb2_grpc
import giveaway_pb2
from fastapi.middleware.cors import CORSMiddleware
import logging
from bot import telegram_bot
from decouple import config

class Item(BaseModel):
    initData: str
app = FastAPI()
origins = [config('DOMAIN')]
logging.basicConfig(level=logging.INFO)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

channel = grpc.aio.insecure_channel(config('GRPC_HOST'))
grpc_stub = giveaway_pb2_grpc.GreeterStub(channel)

def validate(hash_str, init_data, token, c_str="WebAppData"):
    init_data = sorted([ chunk.split("=")
          for chunk in unquote(init_data).replace('==&auth_date=', '%3D%3D&auth_date=').split("&")
            if chunk[:len("hash=")]!="hash="],
        key=lambda x: x[0])
    # TODO: Пофикси этот ужасный костыль
    init_data = "\n".join([f"{rec[0]}={rec[1]}".replace('%3D%3D', '==') for rec in init_data])

    secret_key = hmac.new(c_str.encode(), token.encode(),
        hashlib.sha256 ).digest()
    data_check = hmac.new( secret_key, init_data.encode(),
        hashlib.sha256)

    return data_check.hexdigest() == hash_str

@app.post("/index")
async def index(item: Item):
    initData = {k: v[0] if len(v) == 1 else v for k, v in parse_qs(item.initData).items()}
    if not validate(initData['hash'], item.initData, config('TELEGRAM_TOKEN')):
        logging.info('initData invalid')
        return {'status': 'error', 'message': 'Попробуйте снова'}

    user = json.loads(initData['user'])

    response = await grpc_stub.GetGiveaway(giveaway_pb2.GiveawayRequest(initData=json.dumps(initData)))
    response = json.loads(response.json_message)

    channels = []
    for channel in response['channels']:
        channels.append({**channel, 'subscribed': await telegram_bot.is_user_chat(channel['id'], user['id'])})

    if any(not c['subscribed'] for c in channels):
        return {'status': 'channels_sub', 'channels': channels}

    response = await grpc_stub.ParticipatingGiveaway(giveaway_pb2.GiveawayRequest(initData=json.dumps(initData)))
    response = json.loads(response.json_message)
    if response['status']:
        return {'status': 'success'}
    else:
        return {'status': 'error', 'message': 'Ошибка'}
