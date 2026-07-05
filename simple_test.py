import urllib.request,json,websocket,time
CP=19222
p=json.loads(urllib.request.urlopen(f'http://[::1]:{CP}/json',timeout=3).read())
print('json ok, pages:',len(p))
c=websocket.create_connection(f'ws://[::1]:{CP}/devtools/page/'+p[0]['id'],timeout=5)
print('ws ok')
n=1
def js(cd):
    global n
    n+=1
    c.send(json.dumps({'id':n,'method':'Runtime.evaluate','params':{'expression':cd,'returnByValue':True}}))
    while True:
        r=json.loads(c.recv())
        if r.get('id')==n:
            rs=r.get('result',{})
            if rs.get('isException'):return'EX'
            return str(rs.get('result',{}).get('value',''))

r=js('document.title')
print('title:',r)

# Check page state
ifs=js('''(function(){try{
    var es=document.querySelectorAll("iframe");
    var r=[];
    for(var i=0;i<es.length;i++){
        r.push(es[i].id+" src="+(es[i].src||"").substring(0,50));
    }
    return r.join(" | ");
}catch(e){return"err"}})()''')
print('iframes:',ifs[:500])
c.close()
