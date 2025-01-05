import json

from fastapi import FastAPI
from pydantic import BaseModel
import grpc
import giveaway_pb2_grpc
import giveaway_pb2
from fastapi.middleware.cors import CORSMiddleware

class Item(BaseModel):
    initData: str
    token: str
app = FastAPI()
origins = [
    "https://6cc2-95-105-125-92.ngrok-free.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

channel = grpc.aio.insecure_channel("localhost:50051")
grpc_stub = giveaway_pb2_grpc.GreeterStub(channel)

@app.post("/index")
async def index(item: Item):
    response = await grpc_stub.SayGiveaway(giveaway_pb2.GiveawayRequest(token=item.token, initData=item.initData))

    return json.loads(response.json_message)
