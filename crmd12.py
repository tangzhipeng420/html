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

# First, navigate to fresh state by loading a blank number
ph1='13887724053'

# Type in navframe_133
js('(function(){try{'+
    'var f=document.getElementById('+Q+'navframe_133'+Q+');'+
    'var d=f.contentDocument||f.contentWindow.document;'+
    'var e=d.getElementById('+Q+'ACCESS_NUMBER'+Q+');'+
    'e.value='+Q+ph1+Q+';'+
    'return\"ok\";}catch(e){return\"err\"}})()')
time.sleep(0.5)

# Call the API directly!
r=js('(function(){try{'+
    'var f=document.getElementById('+Q+'navframe_133'+Q+');'+
    'var w=f.contentWindow;'+
    'var obj={};'+
    'obj.ACCESS_NUMBER='+Q+ph1+Q+';'+
    'obj.REMOVE_TAG=$("#REMOVE_TAG",f.contentDocument).val();'+
    'w.agentUtil.ajax({'+
        'url:"AgentCentre.person.payment.IAgentPaymentSV.queryBaseInfoPayment",'+
        'refreshCust:true,'+
        'data:obj,'+
        'success:function(res){'+
            'window.__CDP_RES__=res;'+
        '}'+
    '});'+
    'return\"ok\";}catch(e){return\"err\"}})()')
time.sleep(3)

# Read the result that was stored in window.__CDP_RES__
res=js('(function(){try{return JSON.stringify(window.__CDP_RES__);}catch(e){return\"err\"}})()')
print('=== API RESPONSE ===')
print(res[:3000])

# Also check main page text now
txt=js('(function(){try{return(document.body.innerText||\"\").substring(0,3000);}catch(e){return\"\"}})()')
print('\n=== MAIN PAGE ===')
for line in txt.split('\n'):
    s=line.strip()
    if s and len(s)>1:print(s[:100])

c.close()
