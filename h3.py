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

# First type the search term
js('(function(){try{'+
    'var f=document.getElementById('+Q+'navframe_def'+Q+');'+
    'var d=f.contentDocument;'+
    'd.getElementById("menu_search").value='+Q+'家庭抵用券（权益池）'+Q+';'+
    'return"ok";'+
'}catch(e){return"err"}})()')
time.sleep(1.5)

# Find and click the result
r=js('(function(){try{'+
    'var f=document.getElementById('+Q+'navframe_def'+Q+');'+
    'var d=f.contentDocument;'+
    'var es=d.querySelectorAll("a,li,button,span,div");'+
    'for(var i=0;i<es.length;i++){'+
        'var t=(es[i].innerText||"").trim();'+
        'if(t.indexOf("家庭抵用券")>=0&&t.length<20){'+
            'var e=es[i];'+
            'e.click();'+
            'var info="clicked "+e.tagName+" onclick="+(e.getAttribute("onclick")||e.getAttribute("ontap")||"none");'+
            'return info;'+
        '}'+
    '}'+
    'return"nf";'+
'}catch(e){return"err: "+String(e)}})()')
print('click result:',r)
time.sleep(3)

# Check all iframes for the 权益池 content
for fid in ['navframe_def','navframe_133','navframe_160','navframe_161','navframe_240']:
    txt=js('(function(){try{'+
        'var f=document.getElementById('+Q+fid+Q+');'+
        'if(!f||!f.contentDocument)return"";'+
        'var d=f.contentDocument;'+
        'return(d.body.innerText||"").substring(0,1500);'+
    '}catch(e){return""}})()')
    lines=[l.strip() for l in txt.split('\n') if l.strip() and len(l.strip())>1]
    if lines:
        important=[l for l in lines if any(k in l for k in['权益','抵用券','余额','查询'])]
        if important:
            print(f'\n=== {fid} (important) ===')
            for l in important[:10]:print(l[:150])

# Check CDP targets for new pages
targets=json.loads(urllib.request.urlopen(f'http://[::1]:{CP}/json',timeout=3).read())
print(f'\n=== CDP TARGETS ({len(targets)}) ===')
for t in targets:
    url=t.get('url','')
    if 'agentcentre' in url or 'ordercentre' in url:
        print(f"  {t.get('id','')[:20]}... title={t.get('title','')[:50]} url={url[:100]}")

c.close()
