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

# Get full innerText from navframe_133
txt=js('(function(){try{var f=document.getElementById('+Q+'navframe_133'+Q+');if(!f)return"nf";var d=f.contentDocument||f.contentWindow.document;return(d.body.innerText||"").substring(0,10000);}catch(e){return"err"}})()')
print('=== NAVFRAME_133 FULL TEXT ===')
lines=txt.split('\n')
for l in lines:
    if l.strip():
        print(l.strip()[:200])
print()

# Query button HTML
btn=js('(function(){try{var f=document.getElementById('+Q+'navframe_133'+Q+');if(!f)return"nf";var d=f.contentDocument||f.contentWindow.document;var bs=d.querySelectorAll("button");var r=[];for(var i=0;i<bs.length;i++){r.push(bs[i].outerHTML);}return r.join("|BR|").substring(0,3000);}catch(e){return"err"}})()')
print('=== BUTTONS HTML ===')
for b in btn.split('|BR|'):
    if b.strip():
        print(b[:300])
print()

# Check main page for menu / links
main_links=js('(function(){try{var as=document.querySelectorAll("a");var r=[];for(var i=0;i<as.length;i++){var t=as[i].innerText.trim();if(t&&t.length>1)r.push(t.substring(0,80));}var s=r.join("|SEP|");return s.substring(0,5000);}catch(e){return"err"}})()')
print('=== MAIN PAGE: All link texts ===')
for link in main_links.split('|SEP|'):
    if link.strip():
        print(link.strip()[:100])

c.close()
