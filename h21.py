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

# Navigate
js('document.getElementById("navframe_def").contentWindow.$.search.gotoNav("家庭抵用券（权益池）","/ordercentre/ordercentre?service=page/oc.person.cs.fusion.Equitypoolquery&listener=onInitBusi&MENU_ID=FUSE20210917","",{MENU_ID:"FUSE20210917"})')
time.sleep(3)

# Set phone
ph='15108742724'
js('(function(){try{'+
    'var es=document.querySelectorAll("iframe");'+
    'for(var i=0;i<es.length;i++){'+
        'try{'+
            'var d=es[i].contentDocument;'+
            'if(d&&d.getElementById("ACCESS_NUMBER")){'+
                'd.getElementById("ACCESS_NUMBER").value="'+ph+'";'+
                'var li=d.getElementById("LOGIN_USER_ID");'+
                'if(li){li.value="'+ph+'";li.dispatchEvent(new Event("input",{bubbles:true}));}'+
            '}'+
        '}catch(e){}'+
    '}'+
    'return"ok";'+
'}catch(e){return"ex:"+e.message;}})()')
time.sleep(0.5)

# Query
js('(function(){try{'+
    'var es=document.querySelectorAll("iframe");'+
    'for(var i=0;i<es.length;i++){'+
        'try{'+
            'var d=es[i].contentDocument;'+
            'if(d&&d.getElementById("ACCESS_NUMBER")){'+
                'es[i].contentWindow.checkBaseQuery();'+
            '}'+
        '}catch(e){}'+
    '}'+
    'return"ok";'+
'}catch(e){return"ex:"+e.message;}})()')
time.sleep(2)

# Dump ALL iframe texts
ifs=js('document.querySelectorAll("iframe").length')
for i in range(int(ifs)):
    txt=js(f'(function(){{try{{'+
        f'var f=document.querySelectorAll("iframe")[{i}];'+
        f'var d=f.contentDocument;'+
        f'if(!d)return"no_doc";'+
        f'return f.id+"|BR|"+d.body.innerText.substring(0,4000);'+
    f'}}catch(e){{return"ex:"+e.message;}}}})()')
    if txt and 'no_doc' not in txt and 'ex:' not in txt:
        parts=txt.split('|BR|',1)
        if len(parts)==2:
            print(f'=== {parts[0]} ===')
            for line in parts[1].split('\n'):
                s=line.strip()
                if s:print(s[:200])

c.close()
