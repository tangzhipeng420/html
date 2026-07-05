# -*- coding: utf-8 -*-
import websocket,json,urllib.request,time

p=json.loads(urllib.request.urlopen('http://[::1]:19222/json',timeout=3).read())
c=websocket.create_connection('ws://[::1]:19222/devtools/page/'+p[0]['id'],timeout=5)
c.settimeout(10)
print('CDP connected',flush=True)

n=0
def js(expr):
    global n
    n+=1
    c.send(json.dumps({'id':n,'method':'Runtime.evaluate','params':{'expression':expr,'returnByValue':True}}))
    while 1:
        r=json.loads(c.recv())
        if r.get('id')==n:
            return r.get('result',{}).get('result',{}).get('value','')

print('1+1='+str(js('1+1')),flush=True)

# Check iframes
r=js('(function(){var es=document.querySelectorAll("iframe");return es.length})()')
print(f'Iframes: {r}',flush=True)

# Get title
t=js('document.title')
print(f'Title: {t}',flush=True)

c.close()
print('Done',flush=True)
