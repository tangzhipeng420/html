import websocket,json,urllib.request,time,os,sys
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

# Get main page innerText
txt=js('(function(){try{return(document.body.innerText||\"\").substring(0,30000);}catch(e){return\"\"}})()')
print('=== MAIN PAGE FULL TEXT ===')
lines=txt.split('\n')
for i,l in enumerate(lines):
    s=l.strip()
    if s:print(f'L{i}: {s[:150]}')

c.close()
