from asyncio import sleep
from typing import Coroutine
import aiohttp

PUSH_ENDPOINT = "https://hf.space/embed/dpv/Stage1Recycling/api/queue/push/"
RESULT_ENDPOINT = "https://hf.space/embed/dpv/Stage1Recycling/api/queue/status/"

async def classify_image(source: str) -> Coroutine: 
    payload = {
            "action": "predict", 
            "data": [f"data:image/jpeg;base64,{source}"], 
            "fn_index": 0,
            "session_hash": "q7yir8aa60"
        }
    
    async with aiohttp.ClientSession() as session: 
        async with session.post(PUSH_ENDPOINT, json=payload) as response: 
            hash = await response.json()
            hash = hash["hash"]
            while True:
                async with session.post(RESULT_ENDPOINT, json={"hash": hash}) as res: 
                    data = await res.json()
                    print(data)
                    if data["status"] == "COMPLETE": 
                        return True, data["data"]["data"][0]['label']
                    if data["status"] == "FAILED": 
                        return False, data["status"]
                await sleep(0.2)