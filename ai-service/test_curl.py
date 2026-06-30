import asyncio
import httpx
import json

async def test():
    async with httpx.AsyncClient() as client:
        # 1. Ask analysis
        print("--- REQUEST 1: ANALYSIS ---")
        payload1 = {
            "query": "Analyze Apple",
            "sessionId": "test-sess-1",
            "reportId": None,
            "history": [],
            "currentCompany": None,
            "explainabilityLevel": "Intermediate"
        }
        
        report_id = None
        async with client.stream("POST", "http://127.0.0.1:8000/api/v1/chat/stream", json=payload1) as response:
            async for chunk in response.aiter_text():
                print(chunk)
                if "data: " in chunk:
                    try:
                        data = json.loads(chunk.split("data: ")[1].strip())
                        if data.get("type") == "completed":
                            report_id = data.get("reportId")
                    except:
                        pass
        
        print("\n\nExtracted report_id:", report_id)
        
        if not report_id:
            print("Failed to get reportId")
            return
            
        print("\n--- REQUEST 2: EXPLANATION ---")
        payload2 = {
            "query": "Why hold?",
            "sessionId": "test-sess-1",
            "reportId": report_id,
            "history": [{"role": "user", "content": "Analyze Apple"}],
            "currentCompany": "Apple Inc.",
            "explainabilityLevel": "Intermediate"
        }
        
        async with client.stream("POST", "http://127.0.0.1:8000/api/v1/chat/stream", json=payload2) as response:
            async for chunk in response.aiter_text():
                print(chunk)

if __name__ == "__main__":
    asyncio.run(test())
