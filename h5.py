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

# Get FULL text of navframe_133 and navframe_161 after a number is typed
ph='15108742724'
js('(function(){try{'+
    'var f=document.getElementById('+Q+'navframe_133'+Q+');'+
    'var d=f.contentDocument||f.contentWindow.document;'+
    'd.getElementById('+Q+'ACCESS_NUMBER'+Q+').value='+Q+ph+Q+';'+
    'return"ok";'+
'}catch(e){return"err"}})()')
time.sleep(1.5)

# Get navframe_133 FULL text
txt133=js('(function(){try{'+
    'var f=document.getElementById('+Q+'navframe_133'+Q+');'+
    'var d=f.contentDocument||f.contentWindow.document;'+
    'return(d.body.innerText||"").substring(0,8000);'+
'}catch(e){return"err"}})()')
print('=== NAVFRAME_133 FULL ===')
for line in txt133.split('\n'):
    s=line.strip()
    if s:print(s[:200])

print('\n=== NAVFRAME_161 FULL ===')
txt161=js('(function(){try{'+
    'var f=document.getElementById('+Q+'navframe_161'+Q+');'+
    'var d=f.contentDocument||f.contentWindow.document;'+
    'return(d.body.innerText||"").substring(0,8000);'+
'}catch(e){return"err"}})()')
for line in txt161.split('\n'):
    s=line.strip()
    if s:print(s[:200])

c.close()
