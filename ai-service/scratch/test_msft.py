import json
import httpx
import asyncio

async def test_chat():
    url = "http://localhost:8000/api/v1/chat/stream"
    payload = {
        "query": "analyze MSFT",
        "sessionId": "test_msft"
    }
    
    print(f"Sending POST to {url} with payload: {payload}")
    
    async with httpx.AsyncClient(timeout=300.0) as client:
        async with client.stream("POST", url, json=payload) as response:
            if response.status_code != 200:
                print(f"Failed with status: {response.status_code}")
                content = await response.aread()
                print(content.decode())
                return
                
            print("Connected to SSE stream. Reading events...\n")
            async for line in response.aiter_lines():
                if line:
                    print(line)
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            if data.get("type") == "completed":
                                print("\n--- Report Generated ---")
                                print("Report ID:", data.get("data", {}).get("reportId"))
                        except json.JSONDecodeError:
                            pass

if __name__ == "__main__":
    asyncio.run(test_chat())
