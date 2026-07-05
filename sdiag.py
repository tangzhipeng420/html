import websocket,json,urllib.request,time
URL="http://[::1]:19222/json"
p=json.loads(urllib.request.urlopen(URL,timeout=3).read())
c=websocket.create_connection("ws://[::1]:19222/devtools/page/"+p[0]["id"],timeout=5)
def js(n,cd):
    c.send(json.dumps({"id":n,"method":"Runtime.evaluate","params":{"expression":cd,"returnByValue":True}}))
    time.sleep(0.5)
    r=json.loads(c.recv())
    return r.get("result",{}).get("result",{}).get("value","")

# test eval
print(js(1,"location.href"))
print(js(2,"document.title"))
