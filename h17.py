import websocket,json,urllib.request,time
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
            if rs.get('isException'):return 'EX:'+str(rs.get('exceptionDetails',{}).get('text',''))
            return str(rs.get('result',{}).get('value',''))
Q='"'

# Trigger search
js('(function(){try{'+
    'var d=document.getElementById("navframe_def").contentDocument;'+
    'var e=d.getElementById("menu_search");'+
    'e.value="家庭抵用券（权益池）";'+
    'e.dispatchEvent(new Event("input",{bubbles:true}));'+
    'return"ok";'+
'}catch(e){return"ex:"+e.message;}})()')
time.sleep(2)

# Get ALL elements that contain 家庭抵用券 text - show their HTML
els=js('(function(){try{'+
    'var d=document.getElementById("navframe_def").contentDocument;'+
    'var es=d.querySelectorAll("a,li,button,span,div");'+
    'var r=[];'+
    'for(var i=0;i<es.length;i++){'+
        'var t=(es[i].innerText||"").trim();'+
        'if(t.indexOf("家庭抵用券")>=0&&t.length<50){'+
            'var onclick=es[i].getAttribute("onclick")||es[i].getAttribute("ontap")||"";'+
            'var o=es[i].outerHTML.substring(0,500);'+
            'r.push("TAG="+es[i].tagName+" ONCLICK="+onclick+"\\n"+o);'+
        '}'+
    '}'+
    'return r.join("\\n===\\n");'+
'}catch(e){return"ex:"+e.message;}})()')
print('=== SEARCH RESULT ELEMENTS ===')
print(els[:3000])

c.close()
