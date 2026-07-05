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

# Step 1: Navigate to equity pool
r=js('(function(){try{'+
    'var w=document.getElementById("navframe_def").contentWindow;'+
    'w.$.search.gotoNav('+
        '"家庭抵用券（权益池）",'+
        '"/ordercentre/ordercentre?service=page/oc.person.cs.fusion.Equitypoolquery&listener=onInitBusi&MENU_ID=FUSE20210917",'+
        '"",'+
        '{MENU_ID:"FUSE20210917"}'+
    ');'+
    'return"ok";'+
'}catch(e){return"ex:"+e.message;}})()')
print('nav:',r)
time.sleep(3)

# Step 2: Find the equity pool iframe and set phone
ph='15108742724'
r2=js('(function(){try{'+
    'var es=document.querySelectorAll("iframe");'+
    'for(var i=0;i<es.length;i++){'+
        'try{'+
            'var d=es[i].contentDocument;'+
            'if(d){'+
                'var ac=d.getElementById("ACCESS_NUMBER");'+
                'if(ac){'+
                    'ac.value="'+ph+'";'+
                    'var li=d.getElementById("LOGIN_USER_ID");'+
                    'if(li){li.value="'+ph+'";li.dispatchEvent(new Event("input",{bubbles:true}));}'+
                    'return"phone_set_in_"+es[i].id;'+
                '}'+
            '}'+
        '}catch(e){}'+
    '}'+
    'return"nf";'+
'}catch(e){return"ex:"+e.message;}})()')
print('phone:',r2)
time.sleep(0.5)

# Step 3: Find the equity iframe and call checkBaseQuery
r3=js('(function(){try{'+
    'var es=document.querySelectorAll("iframe");'+
    'for(var i=0;i<es.length;i++){'+
        'try{'+
            'var d=es[i].contentDocument;'+
            'if(d&&d.getElementById("ACCESS_NUMBER")){'+
                'var w=es[i].contentWindow;'+
                'if(w.checkBaseQuery){w.checkBaseQuery();return"query_ok";}'+
            '}'+
        '}catch(e){}'+
    '}'+
    'return"query_nf";'+
'}catch(e){return"ex:"+e.message;}})()')
print('query:',r3)

# Step 4: Wait 1s and read result
time.sleep(1.5)
r4=js('(function(){try{'+
    'var es=document.querySelectorAll("iframe");'+
    'for(var i=0;i<es.length;i++){'+
        'try{'+
            'var d=es[i].contentDocument;'+
            'if(d){'+
                'var txt=d.body.innerText||"";'+
                'if(txt.indexOf("权益池额度")>=0){'+
                    'var lines=txt.split("\\n");'+
                    'for(var j=0;j<lines.length;j++){'+
                        'if(lines[j].indexOf("权益池额度")>=0)'+
                            '{return lines[j].trim();}'+
                    '}'+
                '}'+
            '}'+
        '}catch(e){}'+
    '}'+
    'return"nf";'+
'}catch(e){return"ex:"+e.message;}})()')
print('权益池额度:',r4)

c.close()
