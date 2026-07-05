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

def type_search(text):
    return js('(function(){try{'+
        'var f=document.getElementById('+Q+'navframe_def'+Q+');'+
        'var d=f.contentDocument;'+
        'var e=d.getElementById("menu_search");'+
        'e.value='+Q+text+Q+';'+
        'return"ok";'+
    '}catch(e){return"err"}})()')

# Type in search
kw='家庭抵用券（权益池）'
r=type_search(kw)
print(f'type:{r}')
time.sleep(2)

# Check search results in navframe_def
results=js('(function(){try{'+
    'var f=document.getElementById('+Q+'navframe_def'+Q+');'+
    'var d=f.contentDocument;'+
    'return(d.body.innerText||"").substring(0,3000);'+
'}catch(e){return"err"}})()')
print('=== NAVFRAME_DEF after search ===')
for line in results.split('\n'):
    if line.strip():
        print(line[:200])

# Check menu_search_list for results
lst=js('(function(){try{'+
    'var f=document.getElementById('+Q+'navframe_def'+Q+');'+
    'var d=f.contentDocument;'+
    'var e=d.getElementById("menu_search_list");'+
    'return e?e.innerHTML.substring(0,2000):"nf";'+
'}catch(e){return"err"}})()')
print('\n=== SEARCH LIST ===')
print(lst[:1500])

c.close()
