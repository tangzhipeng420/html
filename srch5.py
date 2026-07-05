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

# Find a/li/button elements with 家庭抵用券
info=js('(function(){try{'+
    'var es=document.querySelectorAll("a,li,button,div");'+
    'var r=[];'+
    'for(var i=0;i<es.length;i++){'+
        'var e=es[i];'+
        'var t=(e.innerText||"").trim();'+
        'if(t.indexOf("家庭抵用券")>=0&&t.length<50){'+
            'var onclick=(e.onclick?e.onclick.toString().substring(0,300):"");'+
            'var href=(e.href||"");'+
            'var tid=(e.id||"");'+
            'var cls=(e.className||"");'+
            'var tag=e.tagName;'+
            'r.push(tag+"/"+tid+"/"+cls+" onclick="+onclick+" href="+href+" html="+t.substring(0,200));'+
        '}'+
    '}'+
    'return r.join("\\n");'+
'}catch(e){return"err: "+String(e)}})()')
print('=== 家庭抵用券 CLICKABLE ===')
print(info[:2000])

c.close()
