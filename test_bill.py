# -*- coding: utf-8 -*-
import websocket,json,urllib.request,time

p=json.loads(urllib.request.urlopen('http://[::1]:19222/json',timeout=3).read())
c=websocket.create_connection('ws://[::1]:19222/devtools/page/'+p[0]['id'],timeout=5)
c.settimeout(10)
print('CDP OK',flush=True)

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

# Find billing iframe
bid=js('(function(){try{var es=document.querySelectorAll("iframe");for(var i=0;i<es.length;i++){try{var d=es[i].contentDocument;if(d&&d.getElementById("ACCESS_NUMBER")){return es[i].id;}}catch(e){}}return"nf";}catch(e){return"err"}})()')
print(f'Bill iframe: {bid}',flush=True)

if bid not in ('nf','err'):
    # Set phone
    ph='15108742724'
    js('document.getElementById("'+bid+'").contentDocument.getElementById("ACCESS_NUMBER").value="'+ph+'"')
    print('Phone set',flush=True)
    time.sleep(0.3)

    # Try billing API
    js('window.__CDP_RES__=null;')
    js('(function(){try{'+
        'var w=document.getElementById("'+bid+'").contentWindow;'+
        'var o={};o.ACCESS_NUMBER="'+ph+'";o.REMOVE_TAG="";'+
        'w.agentUtil.ajax({url:"AgentCentre.person.payment.IAgentPaymentSV.queryBaseInfoPayment",refreshCust:true,data:o,success:function(rr){window.__CDP_RES__=rr;}});'+
        'return"ok";}catch(e){return"err"}})()')
    print('API called, waiting...',flush=True)

    for _ in range(20):
        time.sleep(0.5)
        r=js('window.__CDP_RES__?JSON.stringify(window.__CDP_RES__):null')
        if r and r!='null' and len(r)>20:
            print(f'Got result ({len(r)} chars)',flush=True)
            print(r[:200],flush=True)
            break
    else:
        print('TIMEOUT - no result',flush=True)
else:
    print('No billing iframe found!',flush=True)

c.close()
print('Done',flush=True)
