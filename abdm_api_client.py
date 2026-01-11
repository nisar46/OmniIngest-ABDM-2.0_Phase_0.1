import requests
import json
import time

class ABDMApiClient:
    def __init__(self, client_id, client_secret, gateway_url="https://dev.abdm.gov.in/gateway"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.gateway_url = gateway_url
        self.token = None
        self.token_expiry = 0

    def get_session_token(self):
        """Fetches Bearer Token using Client Credentials Flow"""
        if self.token and time.time() < self.token_expiry:
            return self.token

        url = f"{self.gateway_url}/v0.5/sessions"
        payload = {
            "clientId": self.client_id,
            "clientSecret": self.client_secret
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            self.token = data.get("accessToken")
            # Set expiry to 1 hour (standard for ABDM) - 5 mins buffer
            self.token_expiry = time.time() + 3300 
            print(f"[AUTH] New Bearer Token generated for Client: {self.client_id}")
            return self.token
        except Exception as e:
            print(f"[AUTH ERROR] Failed to get session token: {e}")
            return None

    def profile_share_request(self, abha_id, intent="CONSULTATION"):
        """Initiates M1 Profile Share (v3/profile/share)"""
        token = self.get_session_token()
        if not token:
            return None

        url = f"{self.gateway_url}/v3/profile/share"
        headers = {
            "Authorization": f"Bearer {token}",
            "X-CM-ID": "sbx", # Standard for Sandbox
            "Content-Type": "application/json"
        }
        
        # Note: In a real scenario, we'd generate a fresh requestId (UUID)
        import uuid
        request_id = str(uuid.uuid4())
        
        payload = {
            "requestId": request_id,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()),
            "query": {
                "id": abha_id,
                "purpose": intent,
                "requester": {
                    "type": "HIP",
                    "id": self.client_id
                }
            }
        }

        try:
            print(f"[GATEWAY] Sending Profile Share Request for: {abha_id} (ID: {request_id})")
            response = requests.post(url, headers=headers, json=payload)
            return {"status": "REQUESTED", "requestId": request_id}
        except Exception as e:
            print(f"[GATEWAY ERROR] Profile share failed: {e}")
            return None

# Simple manual test block
if __name__ == "__main__":
    # Placeholder for credentials
    client = ABDMApiClient("YOUR_CLIENT_ID", "YOUR_CLIENT_SECRET")
    # client.get_session_token()
