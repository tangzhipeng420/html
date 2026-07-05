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

# Find the home element - look for 首页 or house icon
info=js('(function(){try{'+
    'var es=document.querySelectorAll("a,li,button,div,span");'+
    'var r=[];'+
    'for(var i=0;i<es.length;i++){'+
        'var e=es[i];'+
        'var t=(e.innerText||"").trim();'+
        'if(t.indexOf("首页")>=0||t.indexOf("home")>=0||t.indexOf("Home")>=0){'+
            'var onclick=(e.onclick?e.onclick.toString().substring(0,200):"");'+
            'var tid=(e.id||"");'+
            'var cls=(e.className||"");'+
            'var tag=e.tagName;'+
            'if(t.length<10)r.push(tag+"/"+tid+"/"+cls+" text="+t+" onclick="+onclick);'+
        '}'+
    '}'+
    'return r.join("\\n");'+
'}catch(e){return"err"}})()')
print('=== HOME ELEMENTS ===')
print(info[:2000])

# Also check navframe_def for 首页 link
def_home=js('(function(){try{'+
    'var f=document.getElementById('+Q+'navframe_def'+Q+');'+
    'if(!f||!f.contentDocument)return"nf";'+
    'var d=f.contentDocument;'+
    'var es=d.querySelectorAll("a,li,button,div,span");'+
    'var r=[];'+
    'for(var i=0;i<es.length;i++){'+
        'var e=es[i];'+
        'var t=(e.innerText||"").trim();'+
        'if(t=="首页"||t=="Home"||t.indexOf("首页")>=0){'+
            'r.push(e.outerHTML.substring(0,400));'+
        '}'+
    '}'+
    'return r.join("\\n===\\n");'+
'}catch(e){return"err"}})()')
print('\n=== HOME IN NAVFRAME_DEF ===')
print(def_home[:2000])

c.close()
