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

# Check what all iframes contain 
for fid in ['navframe_def','navframe_133','navframe_160','navframe_161','leidaFrame','drawerIframe']:
    txt=js('(function(){try{'+
        'var f=document.getElementById('+Q+fid+Q+');'+
        'if(!f||!f.contentDocument)return"";'+
        'var d=f.contentDocument||f.contentWindow.document;'+
        'return(d.body.innerText||"").substring(0,2000);'+
    '}catch(e){return""}})()')
    lines=[l.strip() for l in txt.split('\n') if l.strip()]
    if lines:
        print(f'=== {fid} ({len(lines)} lines) ===')
        for l in lines[:20]:
            print(l[:150])
        print()

c.close()
