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

def type_phone(ph):
    return js('(function(){try{var f=document.getElementById('+Q+'navframe_133'+Q+');var d=f.contentDocument||f.contentWindow.document;var e=d.getElementById('+Q+'ACCESS_NUMBER'+Q+');e.value='+Q+ph+Q+';var ev=new Event(\"input\",{bubbles:true});e.dispatchEvent(ev);return\"ok\";}catch(e){return\"err\"}})()')

# Test with 2 different numbers
phs=['15108742724','13887724053']
for idx,ph in enumerate(phs):
    type_phone(ph)
    time.sleep(2)
    txt=js('(function(){try{return(document.body.innerText||\"\").substring(0,5000);}catch(e){return\"\"}})()')
    print(f'{chr(61)*30} NUM:{ph} {chr(61)*30}')
    for line in txt.split('\n'):
        s=line.strip()
        if s and len(s)>1:
            print(s[:100])
    print()

c.close()
