from asyncio import sleep
from typing import Coroutine
import aiohttp

PUSH_ENDPOINT = "https://hf.space/embed/dpv/Stage1Recycling/api/queue/push/"
RESULT_ENDPOINT = "https://hf.space/embed/dpv/Stage1Recycling/api/queue/status/"

PUSH_ENDPOINT2 = "https://hf.space/embed/dpv/Stage2Recycling/api/queue/push/"
RESULT_ENDPOINT2 = "https://hf.space/embed/dpv/Stage2Recycling/api/queue/status/"

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
                    # print(data)
                    if data["status"] == "COMPLETE": 
                        top_labels, round2 = await process_results(data["data"]["data"][0]['confidences'])
                        if len(round2) > 0: 
                            round2 = await process_round2(round2[0]['confidence'], payload, session)
                            top_labels = top_labels + round2
                            top_labels, _ = await process_results(sorted(top_labels, key=lambda x: x['confidence'], reverse=True))
                            top_labels = map(lambda x: x['label'], top_labels)
                        return True, ["paper" if (x == '2D paper' or x == '3D paper') else x for x in top_labels]
                    if data["status"] == "FAILED": 
                        return False, data["status"]
                await sleep(0.2)

async def process_results(results): 
    highest = results[0]['confidence']
    top_labels = filter(lambda x: highest - x['confidence'] < 0.2, results)
    res = []
    round2 = []
    for x in top_labels: 
        res.append(x) if x['label'] != 'recyc_no_scrap' else round2.append(x)
    return res, round2

async def process_round2(confidence, payload, session): 
    async with session.post(PUSH_ENDPOINT2, json=payload) as response: 
        hash = await response.json()
        # print(hash)
        hash = hash["hash"]
        while True:
            async with session.post(RESULT_ENDPOINT2, json={"hash": hash}) as res: 
                data = await res.json()
                print(data)
                if data["status"] == "COMPLETE": 
                    top_labels, _ = await process_results(data["data"]["data"][0]['confidences'])
                    # total_confidence = sum(map(lambda x: x['confidence'], top_labels))
                    # top_labels = map(lambda x: x[])
                    return top_labels
                if data["status"] == "FAILED": 
                    return [{"label": "Recycleable Items", "confidence": confidence}]
            await sleep(0.2)
