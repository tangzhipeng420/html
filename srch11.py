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

# Check the parent of search tip and find siblings
parent_html=js('(function(){try{'+
    'var e=document.getElementById("searchTip");'+
    'var p=e.parentNode;'+
    'return p.outerHTML.substring(0,4000);'+
'}catch(e){return"err"}})()')
print('=== SEARCHTIP PARENT HTML ===')
print(parent_html)
print()

# Also search for INPUT right before searchTip in DOM order
prev=js('(function(){try{'+
    'var e=document.getElementById("searchTip");'+
    'var pe=e.previousElementSibling;'+
    'return pe?pe.outerHTML.substring(0,2000):"noprev";'+
'}catch(e){return"err"}})()')
print('=== PREVIOUS SIBLING ===')
print(prev)
print()

# Get the full HTML of the top toolbar/header area
header=js('(function(){try{'+
    'var es=document.querySelectorAll("div[class*=header],div[class*=topbar],div[class*=nav],div[class*=toolbar]");'+
    'var r=[];'+
    'for(var i=0;i<es.length;i++){'+
        'r.push(es[i].outerHTML.substring(0,500));'+
    '}'+
    'return r.join("\\n===\\n");'+
'}catch(e){return"err"}})()')
print('=== HEADER AREAS ===')
print(header[:3000])

c.close()
