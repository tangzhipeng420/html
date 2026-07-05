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

# First, find and click the "首页" / 房子 icon on the MAIN page sidebar
home_els=js('(function(){try{'+
    'var es=document.querySelectorAll("a,li,button,div");'+
    'var r=[];'+
    'for(var i=0;i<es.length;i++){'+
        'var e=es[i];'+
        'var t=(e.innerText||"").trim();'+
        'if(t=="首页"||t=="Home"){'+
            'r.push("tag="+e.tagName+" id="+e.id+" class="+e.className+" text="+t);'+
        '}'+
    '}'+
    'return r.join("\\n");'+
'}catch(e){return"err"}})()')
print('=== MAIN PAGE 首页 elements ===')
print(home_els[:1000])

# Click it
r=js('(function(){try{'+
    'var es=document.querySelectorAll("a,li,button,div");'+
    'for(var i=0;i<es.length;i++){'+
        'var t=(es[i].innerText||"").trim();'+
        'if(t=="首页"){'+
            'es[i].click();'+
            'return"clicked "+es[i].tagName;'+
        '}'+
    '}'+
    'return"nf";'+
'}catch(e){return"err"}})()')
print('click:',r)
time.sleep(2)

# NOW type search in navframe_def
js('(function(){try{'+
    'var f=document.getElementById('+Q+'navframe_def'+Q+');'+
    'var d=f.contentDocument;'+
    'var e=d.getElementById("menu_search");'+
    'if(!e)return"search_nf";'+
    'e.value='+Q+'家庭抵用券（权益池）'+Q+';'+
    'return"ok";'+
'}catch(e){return"err"}})()')
time.sleep(1.5)

# Read navframe_def text to confirm
txt=js('(function(){try{'+
    'var f=document.getElementById('+Q+'navframe_def'+Q+');'+
    'var d=f.contentDocument;'+
    'return(d.body.innerText||"").substring(0,3000);'+
'}catch(e){return"err"}})()')
print('\n=== NAVFRAME_DEF after search ===')
for line in txt.split('\n'):
    s=line.strip()
    if s:print(s[:200])

# Check if search results appeared in MAIN page menu_search_list
lst=js('(function(){try{'+
    'var e=document.getElementById("menu_search_list");'+
    'if(!e)return"nf_ct";'+
    'return e.innerHTML.substring(0,2000);'+
'}catch(e){return"err"}})()')
print('\n=== MAIN menu_search_list ===')
print(lst[:1000])

c.close()
