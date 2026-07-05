import websocket,json,urllib.request,base64,time
CP=19222
p=json.loads(urllib.request.urlopen(f'http://[::1]:{CP}/json',timeout=3).read())
c=websocket.create_connection(f'ws://[::1]:{CP}/devtools/page/'+p[0]['id'],timeout=5)
n=1
def js(cd):
    global n
    n+=1
    c.send(json.dumps({'id':n,'method':'Runtime.evaluate','params':{'expression':cd,'returnByValue':True}}))
    while True:
        r=json.loads(c.recv())
        if r.get('id')==n:
            rs=r.get('result',{})
            if rs.get('isException'):return''
            return rs.get('result',{}).get('value','')
Q='"'

# Take screenshot via CDP
n+=1
c.send(json.dumps({'id':n,'method':'Page.captureScreenshot','params':{'format':'png'}}))
while True:
    r=json.loads(c.recv())
    if r.get('id')==n:
        img_b64=r.get('result',{}).get('data','')
        break

with open(r'C:\Users\Administrator\Desktop\权益池页面.png','wb') as f:
    f.write(base64.b64decode(img_b64))
print(f'Screenshot saved: {len(img_b64)//1024}KB')

c.close()
