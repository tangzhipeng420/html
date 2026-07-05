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
Q='"'

# Step 1: Search
js('document.getElementById("navframe_def").contentDocument.getElementById("menu_search").value="家庭抵用券（权益池）"')
time.sleep(1.5)

# Step 2: Click result
r=js('(function(){try{'+
    'var d=document.getElementById("navframe_def").contentDocument;'+
    'var es=d.querySelectorAll("a,li,button,span,div");'+
    'for(var i=0;i<es.length;i++){'+
        'if((es[i].innerText||"").trim().indexOf("家庭抵用券")>=0&&es[i].innerText.length<20)'+
            '{es[i].click();return"ok";}'+
    '}'+
    'return"nf";'+
'}catch(e){return"ex:"+e.message;}})()')
print('click:',r)
time.sleep(3)

# Step 3: List iframes now
ifs=js('(function(){try{'+
    'var es=document.querySelectorAll("iframe");'+
    'var r=[];'+
    'for(var i=0;i<es.length;i++){'+
        'r.push(es[i].id+" disp="+(es[i].style.display||"visible")+" src="+(es[i].src||"").substring(0,60));'+
    '}'+
    'return r.join("\\n");'+
'}catch(e){return"ex:"+e.message;}})()')
print('\n=== IFRAMES ===')
print(ifs[:2000])

# Step 4: Find the one with 权益池 content
for fid in ['navframe_133','navframe_161','navframe_160','navframe_240']:
    txt=js('(function(){try{'+
        'var f=document.getElementById('+Q+fid+Q+');'+
        'if(!f||!f.contentDocument)return"";'+
        'return f.contentDocument.body.innerText.substring(0,200);'+
    '}catch(e){return""}})()')
    if txt and txt!='':
        print(f'{fid}:',txt[:100])

# Step 5: Set phone in whatever iframe has 权益池
# Try all iframes that have contentDocument
all_fids=json.loads('['+'","'.join(['navframe_def','navframe_133','navframe_161','navframe_160','navframe_240','leidaFrame','drawerIframe'])+']')
ph='15108742724'
for fid in all_fids:
    r=js('(function(){try{'+
        'var f=document.getElementById('+Q+fid+Q+');'+
        'if(!f||!f.contentDocument)return"";'+
        'var d=f.contentDocument;'+
        'var ac=d.getElementById("ACCESS_NUMBER");'+
        'var lu=d.getElementById("LOGIN_USER_ID");'+
        'if(ac||lu){'+
            'if(ac)ac.value='+Q+ph+Q+';'+
            'if(lu){lu.value='+Q+ph+Q+';'+
                'lu.dispatchEvent(new Event("input",{bubbles:true}));'+
            '}'+
            'return"found_in_"+'+Q+fid+Q+';'+
        '}'+
        'return"";'+
    '}catch(e){return""}})()')
    if r:print(f'\nACCESS_NUMBER found in {fid}')
if not r:print('\nno ACCESS_NUMBER found in any iframe')

c.close()
