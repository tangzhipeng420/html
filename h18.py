import websocket,json,urllib.request,time
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
            if rs.get('isException'):return 'EX:'+str(rs.get('exceptionDetails',{}).get('text',''))
            return str(rs.get('result',{}).get('value',''))

# Step 1: Navigate to equity pool page via the WADE framework
# This uses the same function the search result click calls
r=js('(function(){try{'+
    'window.$.search.gotoNav('+
        '"家庭抵用券（权益池）",'+
        '"/ordercentre/ordercentre?service=page/oc.person.cs.fusion.Equitypoolquery&listener=onInitBusi&MENU_ID=FUSE20210917",'+
        '"",'+
        '{MENU_ID:"FUSE20210917"}'+
    ');'+
    'return"ok";'+
'}catch(e){return"ex:"+e.message;}})()')
print('gotoNav:',r)
time.sleep(3)

# Step 2: List iframes
ifs=js('(function(){try{'+
    'var es=document.querySelectorAll("iframe");'+
    'var r=[];'+
    'for(var i=0;i<es.length;i++){'+
        'r.push(es[i].id+" disp="+(es[i].style.display||"vis")+" src="+(es[i].src||"").substring(0,80));'+
    '}'+
    'return r.join("|BR|");'+
'}catch(e){return"ex:"+e.message;}})()')
print('IFRAMES:',ifs[:2000])

# Step 3: Find ACCESS_NUMBER
ph='15108742724'
r2=js('(function(){try{'+
    'var es=document.querySelectorAll("iframe");'+
    'for(var i=0;i<es.length;i++){'+
        'try{'+
            'var d=es[i].contentDocument;'+
            'if(d){'+
                'var ac=d.getElementById("ACCESS_NUMBER");'+
                'if(ac){ac.value="'+ph+'";return"ac_in_"+es[i].id;}'+
            '}'+
        '}catch(e){}'+
    '}'+
    'return"nf";'+
'}catch(e){return"ex:"+e.message;}})()')
print('ACCESS_NUMBER:',r2)

c.close()
