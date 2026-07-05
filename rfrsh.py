import urllib.request,json,websocket,time
p=json.loads(urllib.request.urlopen('http://[::1]:19222/json',timeout=3).read())
c=websocket.create_connection('ws://[::1]:19222/devtools/page/'+p[0]['id'],timeout=5)
n=1
def js(cd):
    global n
    n+=1
    c.send(json.dumps({'id':n,'method':'Runtime.evaluate','params':{'expression':cd,'returnByValue':True}}))
    while True:
        r=json.loads(c.recv())
        if r.get('id')==n:
            rs=r.get('result',{})
            if rs.get('isException'):return''
            return rs.get('result',{}).get('value','')

# Step1: reload to get clean state
js('location.reload()')
time.sleep(8)
print('Step1: After reload')
r1=js('(function(){var es=document.querySelectorAll("iframe");var r=[];for(var i=0;i<es.length;i++){r.push(es[i].id+":"+es[i].src.slice(20,70))}return r.join("|")})()')
print('iframes:',r1)

# Step2: navigate to billing
js('document.getElementById("navframe_def").contentWindow.$.search.gotoNav("代收话费","/agentcentre/agentcentre?service=page/oc.person.payment.customer.paymentquery&listener=init&MENU_ID=20210914","",{MENU_ID:"20210914"})')
time.sleep(5)
print('Step2: After nav to billing')
r2=js('(function(){var es=document.querySelectorAll("iframe");var r=[];for(var i=0;i<es.length;i++){r.push(es[i].id+":"+es[i].src.slice(20,100))}return r.join("|")})()')
print('iframes:',r2)

# Step3: try billing API
ph='15108742724'
js('window.__CDP_RES__=null;')
bid=js('(function(){try{var es=document.querySelectorAll("iframe");for(var i=0;i<es.length;i++){try{var d=es[i].contentDocument;if(d&&d.getElementById("ACCESS_NUMBER")&&es[i].src.indexOf("payment")>=0){return es[i].id;}}catch(e){}}return"nf";}catch(e){return"err"}})()')
print('bill iframe:',bid)

if bid!='nf':
    js('(function(){try{'+
        'var d=document.getElementById("'+bid+'").contentDocument;'+
        'd.getElementById("ACCESS_NUMBER").value="'+ph+'";return"ok";}catch(e){return"err"}})()')
    time.sleep(0.3)
    js('(function(){try{'+
        'var w=document.getElementById("'+bid+'").contentWindow;'+
        'var o={};o.ACCESS_NUMBER="'+ph+'";o.REMOVE_TAG="";'+
        'w.agentUtil.ajax({'+
            'url:"AgentCentre.person.payment.IAgentPaymentSV.queryBaseInfoPayment",'+
            'refreshCust:true,data:o,'+
            'success:function(rr){window.__CDP_RES__=rr;}'+
        '});return"ok";}catch(e){return"err"}})()')
    for _ in range(20):
        time.sleep(0.3)
        r=js('window.__CDP_RES__?JSON.stringify(window.__CDP_RES__):null')
        if r and r!='null' and len(r)>20:
            dd=json.loads(r).get('DATA',{})
            print('Name:',dd.get('CUST_NAME'))
            print('Offer:',dd.get('OFFER_NAME'))
            print('Level:',dd.get('GOTONE_LEVEL_NAME'))
            break
    else:
        print('Billing API timed out')
        # Check agentUtil.ajax type
        t=js('typeof document.getElementById("'+bid+'").contentWindow.agentUtil.ajax')
        print('agentUtil.ajax type:',t)
        t2=js('document.getElementById("'+bid+'").contentWindow.agentUtil.ajax.toString().slice(0,200)')
        print('ajax fn:',t2)
else:
    print('No billing iframe found')

c.close()
