import websocket,json,urllib.request,time,os,sys,base64
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

# Get page dimensions then screenshot
n+=1
c.send(json.dumps({'id':n,'method':'Page.getLayoutMetrics','params':{}}))
r=json.loads(c.recv())
while r.get('id')!=n:r=json.loads(c.recv())
cw=r['result']['contentSize']['width']
ch=r['result']['contentSize']['height']
print(f'Page: {cw}x{ch}')

n+=1
c.send(json.dumps({'id':n,'method':'Page.captureScreenshot','params':{'format':'png','clip':{'x':0,'y':0,'width':min(cw,1920),'height':min(ch,1080),'scale':1}}}))
r=json.loads(c.recv())
while r.get('id')!=n:r=json.loads(c.recv())
img_b64=r['result']['data']
with open(os.path.join('C:'+os.sep,'Users','Administrator','Desktop','crm_ss.png'),'wb') as f:
    f.write(base64.b64decode(img_b64))
print(f'Saved {len(img_b64)} bytes to crm_ss.png')
c.close()
