# -*- coding: utf-8 -*-
import websocket,json,urllib.request,time
CP=19222
lg=lambda m:print(time.strftime('%H:%M:%S'),m,flush=True)
try:
    p=json.loads(urllib.request.urlopen('http://[::1]:%d/json'%CP,timeout=3).read())
    c=websocket.create_connection('ws://[::1]:%d/devtools/page/'%CP+p[0]['id'],timeout=5)
except Exception as e:lg('FAIL:'+str(e));exit()
n=0
def js(cd):
    global n;n+=1
    c.send(json.dumps({'id':n,'method':'Runtime.evaluate','params':{'expression':cd,'returnByValue':True}}))
    c.settimeout(5)
    try:
        while True:
            r=json.loads(c.recv())
            if r.get('id')==n:
                rs=r.get('result',{})
                if rs.get('isException'):return''
                return rs.get('result',{}).get('value','')
    except:return ''

# Test billing via navframe_135
fid='navframe_135'
ph='15108742724'
lg('=== BILLING ===')
lg('Setting phone...')
js('document.getElementById("'+fid+'").contentDocument.getElementById("ACCESS_NUMBER").value="'+ph+'"')
lg('Calling API...')
r=js('(function(){try{var w=document.getElementById("'+fid+'").contentWindow;var o={ACCESS_NUMBER:"'+ph+'",REMOVE_TAG:""};window.__CDP_RES__=null;w.agentUtil.ajax({url:"AgentCentre.person.payment.IAgentPaymentSV.queryBaseInfoPayment",refreshCust:true,data:o,success:function(rr){window.__CDP_RES__=rr;}});return"ok";}catch(e){return"err:"+e.message;}})()')
lg('API call: '+r)
time.sleep(3)
r2=js('window.__CDP_RES__?JSON.stringify(window.__CDP_RES__):"null"')
lg('Result: '+str(r2)[:400])

# Test equity via existing equity iframe
lg('=== EQUITY ===')
eqid='eq_17832458716695323'
lg('Using '+eqid)
js('document.getElementById("'+eqid+'").contentDocument.getElementById("ACCESS_NUMBER").value="'+ph+'"')
js('document.getElementById("'+eqid+'").contentDocument.getElementById("LOGIN_USER_ID").value="'+ph+'"')
js('document.getElementById("'+eqid+'").contentDocument.getElementById("LOGIN_USER_ID").dispatchEvent(new Event("input",{bubbles:true}))')
time.sleep(1)
js('document.getElementById("'+eqid+'").contentWindow.checkBaseQuery()')
time.sleep(3)
t=js('document.getElementById("'+eqid+'").contentDocument.body.innerText')
lg('Body: '+str(t[:500] if t else 'null'))
c.close()
