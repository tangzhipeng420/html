# -*- coding: utf-8 -*-
import websocket,json,urllib.request,time

p=json.loads(urllib.request.urlopen('http://[::1]:19222/json',timeout=3).read())
c=websocket.create_connection('ws://[::1]:19222/devtools/page/'+p[0]['id'],timeout=5)
c.settimeout(10)
n=0
def js(e):
    global n;n+=1
    c.send(json.dumps({'id':n,'method':'Runtime.evaluate','params':{'expression':e,'returnByValue':True}}))
    while 1:
        r=json.loads(c.recv())
        if r.get('id')==n:
            rs=r.get('result',{})
            if rs.get('isException'):return'__EXC__'
            return rs.get('result',{}).get('value','')

# Try gotoNav with search text
print('Search 代收话费...',flush=True)
r=js('''document.getElementById("navframe_def").contentWindow.$.search.gotoNav("代收话费")''')
print('Result:',r[:100] if r else 'empty',flush=True)
time.sleep(3)

# Check new iframes
r=js("(function(){var es=document.querySelectorAll('iframe');return Array.from(es).map(function(f){try{var d=f.contentDocument;return f.id+'='+(d?d.title:'-');}catch(e){return f.id+'=ERR'}}).join('|')})()")
print('After nav:',r,flush=True)

# Also try searching for "缴费"
print('Search 缴费...',flush=True)
r=js('''document.getElementById("navframe_def").contentWindow.$.search.gotoNav("缴费")''')
print('Result:',r[:100] if r else 'empty',flush=True)
time.sleep(3)
r=js("(function(){var es=document.querySelectorAll('iframe');return Array.from(es).map(function(f){try{var d=f.contentDocument;return f.id+'='+(d?d.title:'-');}catch(e){return f.id+'=ERR'}}).join('|')})()")
print('After nav2:',r,flush=True)

c.close()
