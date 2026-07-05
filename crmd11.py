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
fn='navframe_133'

# Get checkBaseQuery function source code
src=js('(function(){try{var f=document.getElementById('+Q+fn+Q+');var d=f.contentDocument||f.contentWindow.document;var w=d.defaultView||d.parentWindow;return String(w.checkBaseQuery);}catch(e){return"err"}})()')
print('=== checkBaseQuery ===')
print(src[:2000])
print()

# Also get doCheckBaseQuery
src2=js('(function(){try{var f=document.getElementById('+Q+fn+Q+');var d=f.contentDocument||f.contentWindow.document;var w=d.defaultView||d.parentWindow;return String(w.doCheckBaseQuery);}catch(e){return"err"}})()')
print('=== doCheckBaseQuery ===')
print(src2[:2000])
print()

# Look at how customer info is loaded - search for AJAX calls
scripts=js('(function(){try{var f=document.getElementById('+Q+fn+Q+');var d=f.contentDocument||f.contentWindow.document;var ss=d.querySelectorAll(\"script\");var r=[];for(var i=0;i<ss.length;i++){r.push(ss[i].outerHTML);}return r.join(\"|BR|\");}catch(e){return\"err\"}})()')
print('=== SCRIPTS in navframe ===')
for s in scripts.split('|BR|'):
    if 'ajax' in s.lower() or 'http' in s.lower() or 'query' in s.lower() or 'customer' in s.lower():
        print(s[:500])
        print()

c.close()
