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

# Find ALL input elements on main page with their attributes
html=js('(function(){try{'+
    'var es=document.querySelectorAll("input");'+
    'var r=[];'+
    'for(var i=0;i<es.length;i++){'+
        'var e=es[i];'+
        'var info="id="+(e.id||"")+" placeholder="+(e.placeholder||"")+" type="+(e.type||"")+" class="+(e.className||"")+" onclick="+(e.onclick?e.onclick.toString().substring(0,100):"");'+
        'r.push(info);'+
    '}'+
    'return r.join("\\n");'+
'}catch(e){return"err"}})()')
print('=== ALL MAIN PAGE INPUTS ===')
for line in html.split('\n'):
    if line.strip():
        print(line[:300])

# Also find the search input specifically
srch=js('(function(){try{'+
    'var es=document.querySelectorAll("input[placeholder*=菜单],input[placeholder*=搜索],input[class*=search],input[id*=search],input[id*=menu]");'+
    'var r=[];'+
    'for(var i=0;i<es.length;i++){'+
        'r.push(es[i].outerHTML);'+
    '}'+
    'return r.join("\\n");'+
'}catch(e){return"err"}})()')
print('\n=== SEARCH INPUT ===')
print(srch[:1000])

c.close()
