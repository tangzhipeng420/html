# -*- coding: utf-8 -*-
import websocket,json,urllib.request,time

p=json.loads(urllib.request.urlopen('http://[::1]:19222/json',timeout=3).read())
c=websocket.create_connection('ws://[::1]:19222/devtools/page/'+p[0]['id'],timeout=5)
c.settimeout(10)
n=0
def js(expr):
    global n;n+=1
    c.send(json.dumps({'id':n,'method':'Runtime.evaluate','params':{'expression':expr,'returnByValue':True}}))
    while 1:
        r=json.loads(c.recv())
        if r.get('id')==n:
            rs=r.get('result',{})
            if rs.get('isException'):return'__EXC__'
            return rs.get('result',{}).get('value','')

# Create bill iframe
BILL_URL='/agentcentre/agentcentre?service=page/person.payment.queryBaseInfoPayment&listener=onInitBusi&BEAN_NAME=IAgentPaymentSV&MENU_ID=FUSE20210923'
js("(function(){var f=document.createElement('iframe');f.id='bf2';f.style.display='none';f.src='"+BILL_URL+"';document.body.appendChild(f);return'ok';})()")
time.sleep(5)

# Check bf2 content
r=js("(function(){try{var f=document.getElementById('bf2');var d=f.contentDocument;return d.title+'|'+d.body.innerText.substring(0,200).replace(/\\n/g,' ');}catch(e){return'ERR:'+e.message.substring(0,50)}})()")
print('bf2 content:',r,flush=True)

# Check AN exists
r=js("(function(){try{var f=document.getElementById('bf2');var d=f.contentDocument;return d.getElementById('ACCESS_NUMBER')?'AN_FOUND':'AN_NF';}catch(e){return'ERR:'+e.message.substring(0,50)}})()")
print('bf2 AN:',r,flush=True)

# Check agentUtil
r=js("(function(){try{var f=document.getElementById('bf2');var w=f.contentWindow;return typeof w.agentUtil;}catch(e){return'ERR:'+e.message.substring(0,50)}})()")
print('bf2 agentUtil:',r,flush=True)

# Compare with eqFrame
r=js("(function(){try{var f=document.getElementById('eqFrame');var d=f.contentDocument;return d.getElementById('ACCESS_NUMBER')?'AN_OK':'AN_NF';}catch(e){return'ERR:'+e.message.substring(0,50)}})()")
print('eqFrame AN:',r,flush=True)

# Check what iframes exist
r=js("(function(){var es=document.querySelectorAll('iframe');return Array.from(es).map(function(f){try{var d=f.contentDocument;var t=d?d.title:'-';return f.id+':'+t.substring(0,40);}catch(e){return f.id+':ERR'}}).join('|')})()")
print('All iframes:',r,flush=True)

c.close()
