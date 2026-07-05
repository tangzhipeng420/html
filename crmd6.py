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
fn='navframe_133'

# Type number
ph='15108742724'
r=js('(function(){try{var f=document.getElementById('+Q+fn+Q+');var d=f.contentDocument||f.contentWindow.document;d.getElementById('+Q+'ACCESS_NUMBER'+Q+').value='+Q+ph+Q+';return"ok";}catch(e){return"err"}})()')

# Call queryAll
r=js('(function(){try{var f=document.getElementById('+Q+fn+Q+');var d=f.contentDocument||f.contentWindow.document;var w=d.defaultView||d.parentWindow;w.queryAll();return"ok";}catch(e){return"err"}})()')
print('queryAll:',r)
time.sleep(3)

# Get full body text
txt=js('(function(){try{var f=document.getElementById('+Q+fn+Q+');var d=f.contentDocument||f.contentWindow.document;var t=(d.body.innerText||"").substring(0,10000);return t;}catch(e){return"err"}})()')
print('=== BODY AFTER queryAll ===')
for line in txt.split('\n'):
    if line.strip():
        print(line.strip()[:200])

c.close()
