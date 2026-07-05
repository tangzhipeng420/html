import websocket,json,urllib.request,time
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
            if rs.get('isException'):return 'EX:'+str(rs)
            return str(rs.get('result',{}).get('value',''))
Q='"'

# Test basic CDP
r1=js('1+1')
r2=js('document.title')
r3=js('document.getElementById("navframe_161")?"yes":"no"')

# Set phone
r4=js('(function(){try{'+
    'var d=document.getElementById("navframe_161").contentDocument;'+
    'd.getElementById("ACCESS_NUMBER").value="15108742724";'+
    'd.getElementById("LOGIN_USER_ID").value="15108742724";'+
    'return"ok:"+d.getElementById("ACCESS_NUMBER").value;'+
'}catch(e){return"ex:"+e.message;}})()')

# Call query
time.sleep(0.5)
r5=js('(function(){try{'+
    'var w=document.getElementById("navframe_161").contentWindow;'+
    'w.checkBaseQuery();'+
    'return"ok";'+
'}catch(e){return"ex:"+e.message;}})()')

time.sleep(2)

# Read
r6=js('(function(){try{'+
    'var d=document.getElementById("navframe_161").contentDocument;'+
    'var t=d.body.innerText;'+
    'for(var i=0;i<100;i++){var l=t.split("\\n")[i];if(l&&l.indexOf("权益")>=0)return l;}'+
    'return"nf";'+
'}catch(e){return"ex:"+e.message;}})()')

print('1+1:',r1)
print('title:',r2)
print('nav161 exists:',r3)
print('set:',r4)
print('query:',r5)
print('equity:',r6)

c.close()
