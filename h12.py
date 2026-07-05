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
            if rs.get('isException'):return '__EX:'+rs.get('exceptionDetails',{}).get('text','')
            return rs.get('result',{}).get('value','')
Q='"'

# Step 1: search
js('document.getElementById("navframe_def").contentDocument.getElementById("menu_search").value="家庭抵用券（权益池）"')
time.sleep(1)
# Click result
js('var es=document.getElementById("navframe_def").contentDocument.querySelectorAll("a,li,button,span,div");for(var i=0;i<es.length;i++){if((es[i].innerText||"").trim().indexOf("家庭抵用券")>=0&&es[i].innerText.length<20){es[i].click();break;}}')
time.sleep(2)

# Step 2: Set phone in BOTH fields
r1=js('document.getElementById("navframe_161").contentDocument.getElementById("ACCESS_NUMBER").value="15108742724"')
r2=js('document.getElementById("navframe_161").contentDocument.getElementById("LOGIN_USER_ID").value="15108742724"')
print('set ACCESS:',r1,'set LOGIN:',r2)
time.sleep(0.5)

# Step 3: Call checkBaseQuery from navframe_161 window
r3=js('document.getElementById("navframe_161").contentWindow.checkBaseQuery()')
print('query:',r3)
time.sleep(1.5)

# Step 4: Read result from navframe_133 (main page shows info there)
txt=js('document.getElementById("navframe_161").contentDocument.body.innerText')
print('=== RESULT ===')
for line in txt.split('\n'):
    s=line.strip()
    if '权益' in s or '额度' in s or '余额' in s or '执行' in s:
        print(s[:200])

c.close()
