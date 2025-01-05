from fastapi import FastAPI
from pydantic import BaseModel
import grpc
import giveaway_pb2_grpc
import giveaway_pb2

class Item(BaseModel):
    initData: str
    token: str
app = FastAPI()
channel = grpc.aio.insecure_channel("localhost:50051")
grpc_stub = giveaway_pb2_grpc.GreeterStub(channel)

@app.post("/index")
async def index(item: Item):
    response = await grpc_stub.SayGiveaway(giveaway_pb2.GiveawayRequest(token=item.token, initData=item.initData))

    return {
        "response": response.json_message
    }
