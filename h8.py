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

# Search and click 权益池
js('(function(){try{'+
    'var f=document.getElementById('+Q+'navframe_def'+Q+');'+
    'var d=f.contentDocument;'+
    'd.getElementById("menu_search").value='+Q+'家庭抵用券（权益池）'+Q+';'+
    'return"ok";'+
'}catch(e){return"err"}})()')
time.sleep(1)
js('(function(){try{'+
    'var f=document.getElementById('+Q+'navframe_def'+Q+');'+
    'var d=f.contentDocument;'+
    'var es=d.querySelectorAll("a,li,button,span,div");'+
    'for(var i=0;i<es.length;i++){'+
        'var t=(es[i].innerText||"").trim();'+
        'if(t.indexOf("家庭抵用券")>=0&&t.length<20){'+
            'es[i].click();break;'+
        '}'+
    '}'+
    'return"ok";'+
'}catch(e){return"err"}})()')
time.sleep(2)

# Set phone in BOTH inputs in navframe_161
ph='15108742724'
js('(function(){try{'+
    'var f=document.getElementById('+Q+'navframe_161'+Q+');'+
    'var d=f.contentDocument||f.contentWindow.document;'+
    'd.getElementById("ACCESS_NUMBER").value='+Q+ph+Q+';'+
    'var e=d.getElementById("LOGIN_USER_ID");'+
    'if(e){e.value='+Q+ph+Q+';'+
        'var ev=new Event("input",{bubbles:true});e.dispatchEvent(ev);'+
        'var cv=new Event("change",{bubbles:true});e.dispatchEvent(cv);'+
    '}'+
    'return"ok";'+
'}catch(e){return"err"}})()')
time.sleep(1)

# Click the 执行查询 button which calls checkBaseQuery()
r=js('(function(){try{'+
    'var f=document.getElementById('+Q+'navframe_161'+Q+');'+
    'var d=f.contentDocument||f.contentWindow.document;'+
    'var w=d.defaultView||d.parentWindow;'+
    'w.checkBaseQuery();'+
    'return"ok";'+
'}catch(e){return"err"}})()')
print('query:',r)
time.sleep(3)

# Read 权益池额度
txt=js('(function(){try{'+
    'var f=document.getElementById('+Q+'navframe_161'+Q+');'+
    'var d=f.contentDocument||f.contentWindow.document;'+
    'return(d.body.innerText||"").substring(0,3000);'+
'}catch(e){return"err"}})()')
print('\n=== 权益池额度 ===')
for line in txt.split('\n'):
    s=line.strip()
    if '权益' in s or '额度' in s or '余额' in s:
        print(s[:200])

c.close()
