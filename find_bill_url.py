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
            return rs.get('result',{}).get('value','')

# Try different billing URLs
urls=[
    '/ordercentre/ordercentre?service=page/oc.person.payment.queryBaseInfoPayment&listener=onInitBusi&MENU_ID=FUSE20210923',
    '/agentcentre/agentcentre?service=page/oc.person.payment.queryBaseInfoPayment&listener=onInitBusi&MENU_ID=FUSE20210923',
]

for i,url in enumerate(urls):
    fid='tb'+str(i)
    js("(function(){var f=document.createElement('iframe');f.id='"+fid+"';f.style.display='none';f.src='"+url+"';document.body.appendChild(f);return'ok';})()")
    time.sleep(4)
    r=js("(function(){try{var f=document.getElementById('"+fid+"');var d=f.contentDocument;return d.title+'|'+(d.getElementById('ACCESS_NUMBER')?'AN':'noAN');}catch(e){return d.title+'|ERR:'+e.message.substring(0,30)}})()")
    print(f'URL{i}: {r}',flush=True)

c.close()
