import websocket,json,urllib.request,time
URL="http://[::1]:19222/json"
p=json.loads(urllib.request.urlopen(URL,timeout=3).read())
c=websocket.create_connection("ws://[::1]:19222/devtools/page/"+p[0]["id"],timeout=5)
def js(n,cd):
    c.send(json.dumps({"id":n,"method":"Runtime.evaluate","params":{"expression":cd,"returnByValue":True}}))
    time.sleep(0.5)
    r=json.loads(c.recv())
    return r.get("result",{}).get("result",{}).get("value","")

print("URL:", js(1,"location.href"))
print("TITLE:", js(2,"document.title"))
aids=js(3,"JSON.stringify(Array.from(document.querySelectorAll('iframe'),f=>({id:f.id,src:(f.src||'').slice(0,80)})))")
print("IFRAMES:", aids)
for fn in [x["id"] for x in json.loads(aids or "[]")]:
    v=js(4,"(function(){try{var d=document.getElementById('"+fn+"').contentDocument||document.getElementById('"+fn+"').contentWindow.document;if(!d)return'nope';var e=d.getElementById('ACCESS_NUMBER');return(e?'OK:'+e.value.slice(0,30):'NO_ACCESS: '+d.title.slice(0,120));}catch(e){return'ERR:'+e.message.slice(0,150);}})()")
    print(fn+": "+v[:120])
