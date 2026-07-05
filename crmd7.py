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

# Type a number first to trigger profile display
ph='15108742724'
r=js('(function(){try{var f=document.getElementById('+Q+fn+Q+');var d=f.contentDocument||f.contentWindow.document;d.getElementById('+Q+'ACCESS_NUMBER'+Q+').value='+Q+ph+Q+';return"ok";}catch(e){return"err"}})()')
time.sleep(1)

# Now search MAIN page for 工号 and nearby text
txt=js('(function(){try{var body=document.body;return body.innerText.substring(0,20000);}catch(e){return"err"}})()')
print('=== MAIN PAGE INNER TEXT (searching for 工号 and customer info) ===')
# Find 工号 context
lines=txt.split('\n')
for i,l in enumerate(lines):
    s=l.strip()
    if s and any(k in s for k in ['工号','姓','套餐','ARPU','全球通','姓名','客户','号码：','agent']):
        # Print surrounding lines
        start=max(0,i-2)
        end=min(len(lines),i+5)
        for j in range(start,end):
            if lines[j].strip():
                print(f'  L{j}: {lines[j].strip()[:200]}')
        print('  ---')
print()

# Also get outerHTML of the header/top bar
html=js('(function(){try{var els=document.querySelectorAll(\"div[class*=top],div[class*=header],div[class*=bar],div[id*=top],div[id*=header]\");var r=[];for(var i=0;i<els.length;i++){var t=(els[i].innerText||\"\").substring(0,500);if(t.trim())r.push(t.trim());}return r.join(\"====\").substring(0,3000);}catch(e){return\"err\"}})()')
print('=== TOP BAR ELEMENTS ===')
for h in html.split('===='):
    if h.strip():
        print(h[:300])

# Check document outerHTML for the 工号 element
gonghao=js('(function(){try{var es=document.querySelectorAll(\"*\");for(var i=0;i<es.length;i++){var t=(es[i].innerText||\"\");if(t.indexOf(\"工号\")>=0)return es[i].outerHTML.substring(0,3000);}return\"nof\";}catch(e){return\"err\"}})()')
print('\n=== ELEMENT CONTAINING 工号 ===')
print(gonghao[:2000])

c.close()
