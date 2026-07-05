import urllib.request,json,websocket,time
p=json.loads(urllib.request.urlopen('http://[::1]:19222/json',timeout=3).read())
c=websocket.create_connection('ws://[::1]:19222/devtools/page/'+p[0]['id'],timeout=5)
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

# Check all iframes
ifs=js('(function(){try{'+
    'var es=document.querySelectorAll("iframe");'+
    'var r=[];'+
    'for(var i=0;i<es.length;i++){'+
        'r.push(es[i].id+" src="+(es[i].src||"").substring(0,50));'+
    '}'+
    'return r.join("|BR|");'+
'}catch(e){return"err"}})()')
print(f'IFRAMES: {ifs}')

# Check if nav133 exists
nav133=js('document.getElementById("navframe_133")?"yes":"no"')
print(f'navframe_133: {nav133}')

c.close()
