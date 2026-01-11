from fastapi import FastAPI, Request
from datetime import datetime
import uvicorn
import json
from database_manager import DatabaseManager

app = FastAPI()
db = DatabaseManager()

# Global cache removed (using DB now)

@app.post("/v1/hyp/on-share")
async def on_share_callback(request: Request):
    """Callback endpoint for v3/profile/share"""
    data = await request.json()
    
    # Extract patient profile from payload
    profile = data.get("profile", {})
    abha_id = profile.get("patient", {}).get("id")
    request_id = data.get("resp", {}).get("requestId")

    if abha_id:
        print(f"[WEBHOOK] Received Profile for ABHA: {abha_id}. Saving to Database...")
        db.upsert_patient(
            abha_id=abha_id,
            name=profile.get("patient", {}).get("name"),
            status="ACTIVE",
            notice_date=datetime.now().strftime("%Y-%m-%d"),
            discovery="ABDM_GATEWAY_CALLBACK"
        )
        return {"status": "ACCEPTED"}
    
    return {"status": "FAILED", "reason": "No ABHA_ID found in profile"}

@app.get("/check-profile/{abha_id}")
def check_profile(abha_id: str):
    """Helper for Universal Adapter to check if profile arrived"""
    return PROFILE_CACHE.get(abha_id, {"status": "NOT_FOUND"})

if __name__ == "__main__":
    print("Starting ABDM Webhook Receiver on Port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
