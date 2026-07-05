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

# Get outerHTML of the element
html=js('(function(){try{'+
    'var e=document.getElementById("navtab_2353");'+
    'return e?e.outerHTML.substring(0,2000):"nf";'+
'}catch(e){return"err"}})()')
print('=== LI#navtab_2353 OUTERHTML ===')
print(html)

# Also check all attributes of this element
attrs=js('(function(){try{'+
    'var e=document.getElementById("navtab_2353");'+
    'if(!e)return"nf";'+
    'var r=[];'+
    'for(var i=0;i<e.attributes.length;i++){'+
        'var a=e.attributes[i];'+
        'r.push(a.name+"="+a.value.substring(0,300));'+
    '}'+
    'return r.join("\\n");'+
'}catch(e){return"err"}})()')
print('\n=== ALL ATTRIBUTES ===')
print(attrs)

c.close()
