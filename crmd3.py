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

# Get full innerText from navframe_133 to find ALL text
txt=js('(function(){try{var f=document.getElementById('+Q+'navframe_133'+Q+');if(!f)return"nf";var d=f.contentDocument||f.contentWindow.document;return(d.body.innerText||"").substring(0,8000);}catch(e){return"err"}})()')
print('=== FULL NAVFRAME_133 TEXT ===')
for line in txt.split('\n'):
    l=line.strip()
    if l:
        print(l[:200])
print()

# Also check what other query methods exist in the page JS
# Look at onclick handlers on the 查询 button
js_btn=js('(function(){try{var f=document.getElementById('+Q+'navframe_133'+Q+');if(!f)return"nf";var d=f.contentDocument||f.contentWindow.document;var btn=d.querySelector(\"button\").outerHTML;return btn.substring(0,1000);}catch(e){return"err"}})()')
print('=== QUERY BUTTON HTML ===')
print(js_btn[:500])

# Check main page for target frame info
main_links=js('(function(){try{var as=document.querySelectorAll(\"a\");var r=[];for(var i=0;i<as.length;i++){var t=as[i].innerText.trim();if(t&&t.length>1)r.push(t+\":\"+as[i].href);}return r.join('\n').substring(0,3000);}catch(e){return\"err\"}})()')
print('\n=== MAIN PAGE LINKS ===')
for line in main_links.split('\n'):
    if line.strip():
        print(line[:200])

c.close()
