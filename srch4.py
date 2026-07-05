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

# Find the 家庭抵用券 element HTML
el=js('(function(){try{'+
    'var es=document.querySelectorAll("*");'+
    'for(var i=0;i<es.length;i++){'+
        'var t=(es[i].innerText||"").trim();'+
        'if(t.indexOf("家庭抵用券")>=0||t.indexOf("权益池")>=0){'+
            'return es[i].outerHTML.substring(0,2000);'+
        '}'+
    '}'+
    'return"nf";'+
'}catch(e){return"err"}})()')
print('=== 家庭抵用券 ELEMENT ===')
print(el[:2000])
print()

# Get the onclick handler
clickinfo=js('(function(){try{'+
    'var es=document.querySelectorAll("*");'+
    'for(var i=0;i<es.length;i++){'+
        'var t=(es[i].innerText||"").trim();'+
        'if(t.indexOf("家庭抵用券")>=0){'+
            'var e=es[i];'+
            'var info="tag="+e.tagName+" onclick="+(e.onclick?e.onclick.toString().substring(0,300):"none")+" href="+(e.href||"none");'+
            'return info;'+
        '}'+
    '}'+
    'return"nf";'+
'}catch(e){return"err"}})()')
print('=== CLICK INFO ===')
print(clickinfo)

c.close()
