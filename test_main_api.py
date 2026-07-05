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

# Check agentUtil in main page
r=js('typeof window.agentUtil')
print('main agentUtil:',r,flush=True)

# Try navframe_133 which has some content - check agentUtil there
r=js("typeof document.getElementById('navframe_133').contentWindow.agentUtil")
print('nav133 agentUtil:',r,flush=True)

# Try equity iframe
r=js("typeof document.getElementById('ef').contentWindow.agentUtil")
print('ef agentUtil:',r,flush=True)

# Try billing API from equity iframe
ph='15108742724'
js('window.__CDP_RES__=null;')
js("(function(){try{var w=document.getElementById('ef').contentWindow;var o={ACCESS_NUMBER:'"+ph+"',REMOTE_TAG:''};w.agentUtil.ajax({url:'AgentCentre.person.payment.IAgentPaymentSV.queryBaseInfoPayment',refreshCust:true,data:o,success:function(rr){window.__CDP_RES__=rr;}});return'ok';}catch(e){return'err'}})()")
print('API called from ef, waiting...',flush=True)
got=False
for _ in range(15):
    time.sleep(0.5)
    r=js('window.__CDP_RES__?JSON.stringify(window.__CDP_RES__):null')
    if r and r!='null' and len(r)>20:
        print(f'Got: {r[:200]}',flush=True)
        got=True
        break
if not got:
    print('No result from ef agentUtil',flush=True)

c.close()
