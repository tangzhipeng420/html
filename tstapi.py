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
            if rs.get('isException'):return ''
            return rs.get('result',{}).get('value','')

ph='15108742724'
js('window.__CDP_RES__=null;')
js('(function(){try{'+
    'var o={};o.ACCESS_NUMBER="'+ph+'";o.REMOVE_TAG="";'+
    'window.agentUtil.ajax({'+
        'url:"AgentCentre.person.payment.IAgentPaymentSV.queryBaseInfoPayment",'+
        'refreshCust:true,'+
        'data:o,'+
        'success:function(rr){window.__CDP_RES__=rr;}'+
    '});return"ok";}catch(e){return"err";}})()')
for _ in range(15):
    time.sleep(0.3)
    r=js('window.__CDP_RES__?JSON.stringify(window.__CDP_RES__):null')
    if r and r!='null' and len(r)>20:
        dd=json.loads(r).get('DATA',{})
        print('CUST_NAME:',dd.get('CUST_NAME'))
        print('OFFER_NAME:',dd.get('OFFER_NAME'))
        print('GOTONE_LEVEL_NAME:',dd.get('GOTONE_LEVEL_NAME'))
        print('GOTONE_MONTH_ARPU:',dd.get('GOTONE_MONTH_ARPU'))
        print('GOTONE_YEAR_ARPU:',dd.get('GOTONE_YEAR_ARPU'))
        break
else:print('TIMEOUT - no data')
c.close()
