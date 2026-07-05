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
            if rs.get('isException'):return 'EX:'+str(rs)
            return str(rs.get('result',{}).get('value',''))
Q='"'

# First list all iframes
all_ifs=js('(function(){try{'+
    'var es=document.querySelectorAll("iframe");'+
    'var r=[];'+
    'for(var i=0;i<es.length;i++){'+
        'var e=es[i];'+
        'r.push(e.id+" src="+(e.src||"").substring(0,80)+" style="+(e.style.display||""));'+
    '}'+
    'return r.join("\\n");'+
'}catch(e){return"ex:"+e.message;}})()')
print('=== ALL IFRAMES NOW ===')
print(all_ifs[:2000])

# Also check if navframe_133 exists
nav133=js('document.getElementById("navframe_133")?"yes":"no"')
print('navframe_133:',nav133)

c.close()
