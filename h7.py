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

# First: search and click 权益池
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

# Get navframe_161 HTML to find the correct input and button
inputs=js('(function(){try{'+
    'var f=document.getElementById('+Q+'navframe_161'+Q+');'+
    'var d=f.contentDocument||f.contentWindow.document;'+
    'var es=d.querySelectorAll("input,button,select");'+
    'var r=[];'+
    'for(var i=0;i<es.length;i++){'+
        'var e=es[i];'+
        'r.push(e.outerHTML.substring(0,500));'+
    '}'+
    'return r.join("\\n====\\n").substring(0,5000);'+
'}catch(e){return"err"}})()')
print('=== INPUTS/BUTTONS in navframe_161 ===')
print(inputs[:4000])

c.close()
