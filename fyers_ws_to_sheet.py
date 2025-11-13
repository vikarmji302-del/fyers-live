import json, time, requests, websocket

# === Fill these three ===
FY_APP_ID = "YOUR_APP_ID"
FY_ACCESS_TOKEN = "YOUR_ACCESS_TOKEN"
APPS_SCRIPT_URL = "https://script.google.com/macros/s/XXXXXXXX/exec"
# ========================

# Choose your option symbols
SYMBOLS = ["NFO:NIFTY24NOV24000CE", "NFO:NIFTY24NOV24000PE"]

def post_to_sheet(payload):
    try:
        r = requests.post(APPS_SCRIPT_URL, json=payload, timeout=8)
        print("POST ->", r.status_code)
    except Exception as e:
        print("POST error:", e)

def on_message(ws, message):
    print("RAW:", message)
    try:
        data = json.loads(message)
    except:
        return

    symbol = data.get("symbol")
    ltp = data.get("ltp") or data.get("lt")
    volume = data.get("volume")

    payload = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": symbol,
        "ltp": ltp,
        "volume": volume,
        "raw": data
    }
    post_to_sheet(payload)

def on_open(ws):
    print("✅ WebSocket opened")
    sub_payload = {"T": "SUB_LTP", "symbols": SYMBOLS}
    ws.send(json.dumps(sub_payload))
    print("Subscribed to", SYMBOLS)

def on_error(ws, error):
    print("Error:", error)

def on_close(ws, *args):
    print("Closed, reconnecting in 5s...")
    time.sleep(5)
    start_ws()

def start_ws():
    ws_url = "wss://datafeed.fyers.in/socket/v2/ws"
    headers = [f"Authorization: Bearer {FY_ACCESS_TOKEN}"]
    ws = websocket.WebSocketApp(ws_url,
                                header=headers,
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.run_forever(ping_interval=20, ping_timeout=10)

if __name__ == "__main__":
    print("Starting Fyers → Google Sheet bridge")
    start_ws()
