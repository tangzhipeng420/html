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

# Find search bar on main page
html=js('(function(){try{'+
    'var es=document.querySelectorAll("input[type=text],input[placeholder*=搜索],input[placeholder*=search],div[class*=search],div[id*=search]");'+
    'var r=[];'+
    'for(var i=0;i<es.length;i++){'+
        'var o=es[i].outerHTML||"";'+
        'r.push(o.substring(0,500));'+
    '}'+
    'return r.join("======");'+
'}catch(e){return"err"}})()')
print('=== SEARCH INPUTS ===')
for h in html.split('======'):
    if h.strip():print(h[:400])

# Also check navframe_def for search
html2=js('(function(){try{'+
    'var f=document.getElementById('+Q+'navframe_def'+Q+');'+
    'if(!f||!f.contentDocument)return"nf";'+
    'var d=f.contentDocument;'+
    'return(d.body.innerText||"").substring(0,3000);'+
'}catch(e){return"err"}})()')
print('\n=== NAVFRAME_DEF ===')
for line in html2.split('\n'):
    s=line.strip()
    if s:print(s[:200])

# Look for search bar in all iframes
for fid in ['navframe_def','navframe_133','navframe_160','navframe_161']:
    html3=js('(function(){try{'+
        'var f=document.getElementById('+Q+fid+Q+');'+
        'if(!f||!f.contentDocument)return"";'+
        'var d=f.contentDocument;'+
        'var es=d.querySelectorAll("input");'+
        'var r=[];'+
        'for(var i=0;i<es.length;i++){'+
            'var p=es[i].placeholder||"";'+
            'var t=es[i].type||"";'+
            'var i2=es[i].id||"";'+
            'if(p||i2)r.push(fid+":"+t+":"+i2+":"+p);'+
        '}'+
        'return r.join(" | ");'+
    '}catch(e){return""}})()')
    if html3.strip():
        print(f'\n=== INPUTS in {fid} ===')
        print(html3[:1000])

c.close()
