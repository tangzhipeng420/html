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

# Step 1: search + click
js('(function(){try{'+
    'var f=document.getElementById('+Q+'navframe_def'+Q+');'+
    'f.contentDocument.getElementById("menu_search").value='+Q+'家庭抵用券（权益池）'+Q+';'+
    'return"ok";'+
'}catch(e){return"err"}})()')
time.sleep(1)
js('(function(){try{'+
    'var f=document.getElementById('+Q+'navframe_def'+Q+');'+
    'var es=f.contentDocument.querySelectorAll("a,li,button,span,div");'+
    'for(var i=0;i<es.length;i++){'+
        'if((es[i].innerText||"").trim().indexOf("家庭抵用券")>=0&&es[i].innerText.length<20)'+
            '{es[i].click();break;}'+
    '}'+
    'return"ok";'+
'}catch(e){return"err"}})()')
time.sleep(2)

# Step 2: Type phone using jQuery .val() to trigger WADE events
ph='15108742724'
r=js('(function(){try{'+
    'var f=document.getElementById('+Q+'navframe_161'+Q+');'+
    'var w=f.contentWindow;'+
    'var d=f.contentDocument||f.contentWindow.document;'+
    '// Use jQuery to set value (triggers change events)'+
    'var ph='+Q+ph+Q+';'+
    'd.getElementById("ACCESS_NUMBER").value=ph;'+
    'var li=d.getElementById("LOGIN_USER_ID");'+
    'if(li){li.value=ph;'+
        'var e1=new Event("input",{bubbles:true});li.dispatchEvent(e1);'+
        'var e2=new Event("change",{bubbles:true});li.dispatchEvent(e2);'+
        'var e3=new Event("keyup",{bubbles:true});li.dispatchEvent(e3);'+
    '}'+
    'return"ok";'+
'}catch(e){return"err: "+String(e)}})()')
print('type:',r)
time.sleep(0.5)

# Step 3: Click 执行查询
r=js('(function(){try{'+
    'var f=document.getElementById('+Q+'navframe_161'+Q+');'+
    'var w=f.contentWindow;'+
    'w.checkBaseQuery();'+
    'return"ok";'+
'}catch(e){return"err: "+String(e)}})()')
print('query:',r)

# Step 4: Wait 1.5 seconds for data to load
time.sleep(1.5)

# Step 5: Read 权益池额度
quanyi=js('(function(){try{'+
    'var f=document.getElementById('+Q+'navframe_161'+Q+');'+
    'var d=f.contentDocument||f.contentWindow.document;'+
    'var txt=d.body.innerText||"";'+
    'var lines=txt.split("\\n");'+
    'for(var i=0;i<lines.length;i++){'+
        'if(lines[i].indexOf("权益池额度")>=0)'+
            '{return lines[i].substring(0,200);}'+
    '}'+
    'return"nf";'+
'}catch(e){return"err"}})()')
print('权益池额度:',quanyi)

# Also get the main page body around app level for any result
app=js('(function(){try{'+
    'var f=document.getElementById('+Q+'navframe_161'+Q+');'+
    'var d=f.contentDocument||f.contentWindow.document;'+
    'var es=d.querySelectorAll("[class*=quanyi],[class*=amount],[class*=equity]");'+
    'var r=[];'+
    'for(var i=0;i<es.length;i++){'+
        'r.push(es[i].outerHTML.substring(0,200));'+
    '}'+
    'return r.join("\\n");'+
'}catch(e){return""}})()')
if app:print('quanyi el:',app[:500])

c.close()
