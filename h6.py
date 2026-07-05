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

# Step 1: Search 权益池 in navframe_def
js('(function(){try{'+
    'var f=document.getElementById('+Q+'navframe_def'+Q+');'+
    'var d=f.contentDocument;'+
    'd.getElementById("menu_search").value='+Q+'家庭抵用券（权益池）'+Q+';'+
    'return"ok";'+
'}catch(e){return"err"}})()')
time.sleep(1)

# Step 2: Click result
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

# Step 3: Type phone in navframe_161
ph='15108742724'
r=js('(function(){try{'+
    'var f=document.getElementById('+Q+'navframe_161'+Q+');'+
    'var d=f.contentDocument||f.contentWindow.document;'+
    'var es=d.querySelectorAll("input");'+
    'for(var i=0;i<es.length;i++){'+
        'var e=es[i];'+
        'if(e.type=="text"&&(e.id.indexOf("service")>=0||e.id.indexOf("ACCESS")>=0)){'+
            'e.value='+Q+ph+Q+';break;'+
        '}'+
    '}'+
    'return"ok";'+
'}catch(e){return"err"}})()')
print('type:',r)
time.sleep(1)

# Step 4: Click 执行查询 button
r=js('(function(){try{'+
    'var f=document.getElementById('+Q+'navframe_161'+Q+');'+
    'var d=f.contentDocument||f.contentWindow.document;'+
    'var es=d.querySelectorAll("button,a,li,input");'+
    'for(var i=0;i<es.length;i++){'+
        'var t=(es[i].innerText||es[i].value||"").trim();'+
        'if(t.indexOf("执行查询")>=0){es[i].click();return"ok";}'+
    '}'+
    'return"nf";'+
'}catch(e){return"err"}})()')
print('click query btn:',r)
time.sleep(3)

# Step 5: Read 权益池额度
txt=js('(function(){try{'+
    'var f=document.getElementById('+Q+'navframe_161'+Q+');'+
    'var d=f.contentDocument||f.contentWindow.document;'+
    'return(d.body.innerText||"").substring(0,5000);'+
'}catch(e){return"err"}})()')
print('\n=== NAVFRAME_161 - 权益相关 ===')
for line in txt.split('\n'):
    s=line.strip()
    if s and ('权益' in s or '抵用' in s or '额度' in s or '余额' in s or '执行' in s):
        print(s[:200])

c.close()
