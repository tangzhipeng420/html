import urllib.request, json
pages = json.loads(urllib.request.urlopen("http://127.0.0.1:19222/json", timeout=5).read())
for i, p in enumerate(pages):
    pid = p["id"][:16]
    title = (p.get("title","") or "")[:60]
    print(f"[{i}] {pid}... {title}")
print(f"Total: {len(pages)} pages")
# Check each page for iframes
import websocket, time
for i, p in enumerate(pages):
    try:
        ws = websocket.create_connection(f"ws://127.0.0.1:19222/devtools/page/{p['id']}", timeout=5)
        ws.send(json.dumps({"id":1,"method":"Runtime.evaluate","params":{"expression":"document.querySelectorAll('iframe').length","returnByValue":True}}))
        time.sleep(1)
        r = json.loads(ws.recv())
        frames = r.get("result",{}).get("value","?")
        print(f"[{i}] {title}: {frames} iframes")
        ws.close()
    except Exception as e:
        print(f"[{i}] {title}: ERROR {e}")
