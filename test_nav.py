# -*- coding: utf-8 -*-
import websocket,json,urllib.request,time

p=json.loads(urllib.request.urlopen('http://[::1]:19222/json',timeout=3).read())
c=websocket.create_connection('ws://[::1]:19222/devtools/page/'+p[0]['id'],timeout=5)
c.settimeout(10)

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

# Navigate to payment page
print('Nav to payment...',flush=True)
r=js('document.getElementById("navframe_def").contentWindow.$.search.gotoNav("代收话费","/agentcentre/agentcentre?service=page/person.payment.queryBaseInfoPayment&listener=onInitBusi&BEAN_NAME=IAgentPaymentSV&TITLE=%E4%BB%A3%E6%94%B6%E8%AF%9D%E8%B4%B9&MENU_ID=FUSE20210923","",{MENU_ID:"FUSE20210923"})')
print('Nav result:',str(r)[:100],flush=True)
time.sleep(3)

# List frames again
r=js("(function(){try{var es=document.querySelectorAll(\"iframe\");var out=[];for(var i=0;i<es.length;i++){try{var d=es[i].contentDocument;var an=d&&d.getElementById(\"ACCESS_NUMBER\")?\"AN\":\"-\";out.push(es[i].id+\"=\"+an);}catch(e){out.push(es[i].id+\"=ERR\")}}return out.join(\"|\");}catch(e){return\"ERR\"}})()")
print('Frames:',r,flush=True)

# Find billing iframe
bid=js("(function(){try{var es=document.querySelectorAll(\"iframe\");for(var i=0;i<es.length;i++){try{var d=es[i].contentDocument;if(d&&d.getElementById(\"ACCESS_NUMBER\")&&d.defaultView&&d.defaultView.agentUtil){return es[i].id;}}catch(e){}}return\"nf\";}catch(e){return\"err\"}})()")
print(f'Bill iframe: {bid}',flush=True)

c.close()
