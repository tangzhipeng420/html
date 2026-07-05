import websocket,json,urllib.request,time,os,sys
CP=19222
p=json.loads(urllib.request.urlopen(f'http://[::1]:{CP}/json',timeout=3).read())
c=websocket.create_connection(f'ws://[::1]:{CP}/devtools/page/'+p[0]['id'],timeout=5)
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
Q='"'

# Type phone in ACCESS_NUMBER
ph='15108742724'
r=js('(function(){try{'+
    'var f=document.getElementById('+Q+'navframe_133'+Q+');'+
    'var d=f.contentDocument||f.contentWindow.document;'+
    'd.getElementById('+Q+'ACCESS_NUMBER'+Q+').value='+Q+ph+Q+';'+
    'return"ok";'+
'}catch(e){return"err"}})()')
print('type:',r)
time.sleep(1)

# Call the billing API to refresh
js('(function(){try{'+
    'var f=document.getElementById('+Q+'navframe_133'+Q+');'+
    'var w=f.contentWindow;'+
    'var obj={};'+
    'obj.ACCESS_NUMBER='+Q+ph+Q+';'+
    'obj.REMOVE_TAG="";'+
    'w.agentUtil.ajax({'+
        'url:"AgentCentre.person.payment.IAgentPaymentSV.queryBaseInfoPayment",'+
        'refreshCust:true,'+
        'data:obj,'+
        'success:function(res){'+
            'window.__CDP_RES__=res;'+
        '}'+
    '});'+
    'return"ok";'+
'}catch(e){return"err"}})()')
time.sleep(3)

# Read navframe_133 text for 权益池额度
txt=js('(function(){try{'+
    'var f=document.getElementById('+Q+'navframe_133'+Q+');'+
    'var d=f.contentDocument||f.contentWindow.document;'+
    'return(d.body.innerText||"").substring(0,5000);'+
'}catch(e){return"err"}})()')
print('\n=== NAVFRAME_133 after query ===')
for line in txt.split('\n'):
    s=line.strip()
    if s and ('权益' in s or '抵用' in s or '额度' in s or '余额' in s or '查询' in s):
        print(s[:200])

# Also check the main page for权益池 info
main=js('(function(){try{return(document.body.innerText||"").substring(0,3000);}catch(e){return""}})()')
print('\n=== MAIN PAGE (权益相关) ===')
for line in main.split('\n'):
    s=line.strip()
    if s and ('权益' in s or '抵用' in s or '额度' in s):
        print(s[:200])

c.close()
