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

# Get full HTML of menu_search area and nearby elements
# Find the search bar - look at elements above searchTip
html=js('(function(){try{'+
    'var e=document.getElementById("searchTip");'+
    'if(!e)return"nf";'+
    'var p=e.parentNode;'+
    'return p.innerHTML.substring(0,3000);'+
'}catch(e){return"err"}})()')
print('=== SEARCHTIP PARENT HTML ===')
print(html)
print()

# Also look at the verifyInput area - might be the search bar
vhtml=js('(function(){try{'+
    'var e=document.getElementById("verifyInput");'+
    'if(!e)return"nf";'+
    'var p=e.parentNode;'+
    'return p.innerHTML.substring(0,3000);'+
'}catch(e){return"err"}})()')
print('=== VERIFYINPUT PARENT HTML ===')
print(vhtml)

c.close()
