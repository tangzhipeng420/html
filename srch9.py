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

# Get ALL visible text on main page and look for 搜索
txt=js('(function(){try{return(document.body.innerText||\"\").substring(0,10000);}catch(e){return\"\"}})()')
lines=txt.split('\n')
for i,l in enumerate(lines):
    s=l.strip()
    if s and ('搜索' in s or '热门' in s or '搜索' in s):
        print(f'L{i}: {s[:200]}')

# Also look at elements with class containing search
cls=js('(function(){try{'+
    'var es=document.querySelectorAll("[class*=search],[id*=search],[class*=Search],[id*=Search]");'+
    'var r=[];'+
    'for(var i=0;i<es.length;i++){'+
        'var e=es[i];'+
        'r.push(e.tagName+" id="+(e.id||"")+" class="+(e.className||"")+" text="+((e.innerText||"").trim().substring(0,50))+" ph="+(e.placeholder||""));'+
    '}'+
    'return r.join("\\n");'+
'}catch(e){return"err"}})()')
print('\n=== SEARCH-RELATED ELEMENTS ===')
print(cls[:2000])

c.close()
