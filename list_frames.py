# -*- coding: utf-8 -*-
import websocket,json,urllib.request,time

p=json.loads(urllib.request.urlopen('http://[::1]:19222/json',timeout=3).read())
c=websocket.create_connection('ws://[::1]:19222/devtools/page/'+p[0]['id'],timeout=5)
c.settimeout(10)

n=0
def js(expr):
    global n
    n+=1
    c.send(json.dumps({'id':n,'method':'Runtime.evaluate','params':{'expression':expr,'returnByValue':True}}))
    while 1:
        r=json.loads(c.recv())
        if r.get('id')==n:
            rs=r.get('result',{})
            if rs.get('isException'):return '__EXC__'
            return rs.get('result',{}).get('value','')

# List all iframes
r=js('(function(){try{var es=document.querySelectorAll("iframe");var out=[];for(var i=0;i<es.length;i++){try{var d=es[i].contentDocument;var hasAN=d&&d.getElementById("ACCESS_NUMBER")?"AN":"noAN";var hasLU=d&&d.getElementById("LOGIN_USER_ID")?"LU":"noLU";var hasAU=d&&d.getElementById("ACCESS_NUMBER")&&d.defaultView&&d.defaultView.agentUtil?"AU":"noAU";var src=es[i].src||"";src=src.substring(0,80);out.push(es[i].id+"|AN="+hasAN+"|LU="+hasLU+"|AU="+hasAU+"|src="+src);}catch(e){out.push(es[i].id+"|ERROR="+e.message.substring(0,30))}}return out.join("||");}catch(e){return"ERR:"+e.message}})()')
print('Frames:',flush=True)
for line in r.split('||'):
    print('  '+line,flush=True)

c.close()
