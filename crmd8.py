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
fn='navframe_133'

# Test approach: trigger events properly
def type_and_trigger(ph):
    """Clear, set value, fire events"""
    return js('(function(){try{var f=document.getElementById('+Q+fn+Q+');var d=f.contentDocument||f.contentWindow.document;var e=d.getElementById('+Q+'ACCESS_NUMBER'+Q+');if(!e)return\"noe\";e.value='+Q+ph+Q+';var ev=new Event(\"input\",{bubbles:true});e.dispatchEvent(ev);return\"ok\";}catch(e){return\"err\"}})()')

# Test 1: type first number, check main page
ph1='15108742724'
r=type_and_trigger(ph1)
time.sleep(2)
txt=js('(function(){try{return(document.body.innerText||\"\").substring(0,3000);}catch(e){return\"\"}})()')
lines=txt.split('\n')
for i,l in enumerate(lines):
    s=l.strip()
    if any(k in s for k in['客户姓名','服务号码','主套餐','ARPU','全球通','SIM','归属']):
        val=lines[i+1].strip() if i+1<len(lines) else''
        print(f'T1 L{i}: {s} {val}', flush=True)

print('---',flush=True)
# Test 2: type second number, check main page
ph2='13887724053'
r=type_and_trigger(ph2)
time.sleep(2)
txt=js('(function(){try{return(document.body.innerText||\"\").substring(0,3000);}catch(e){return\"\"}})()')
lines=txt.split('\n')
for i,l in enumerate(lines):
    s=l.strip()
    if any(k in s for k in['客户姓名','服务号码','主套餐','ARPU','全球通','SIM','归属']):
        val=lines[i+1].strip() if i+1<len(lines) else''
        print(f'T2 L{i}: {s} {val}', flush=True)

print('---',flush=True)
# Try also firing keypress Enter event
ph3='13577710548'
r=js('(function(){try{var f=document.getElementById('+Q+fn+Q+');var d=f.contentDocument||f.contentWindow.document;var e=d.getElementById('+Q+'ACCESS_NUMBER'+Q+');e.value='+Q+ph3+Q+';var ev=new KeyboardEvent(\"keypress\",{key:\"Enter\",keyCode:13,which:13,bubbles:true});e.dispatchEvent(ev);return\"ok\";}catch(e){return\"err\"}})()')
time.sleep(2)
txt=js('(function(){try{return(document.body.innerText||\"\").substring(0,3000);}catch(e){return\"\"}})()')
lines=txt.split('\n')
for i,l in enumerate(lines):
    s=l.strip()
    if any(k in s for k in['客户姓名','服务号码','主套餐','ARPU','全球通','SIM','归属']):
        val=lines[i+1].strip() if i+1<len(lines) else''
        print(f'T3 L{i}: {s} {val}', flush=True)

c.close()
