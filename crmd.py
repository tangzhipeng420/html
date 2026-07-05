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
ph='15108742724'
# Type number
r=js('(function(){try{var f=document.getElementById('+Q+fn+Q+');var d=f.contentDocument||f.contentWindow.document;d.getElementById('+Q+'ACCESS_NUMBER'+Q+').value='+Q+ph+Q+';return"ok";}catch(e){return"err"}})()')
print('type:',r)
time.sleep(0.5)
# Click query
r=js('(function(){try{var f=document.getElementById('+Q+fn+Q+');var d=f.contentDocument||f.contentWindow.document;var bs=d.querySelectorAll("button");for(var i=0;i<bs.length;i++){if(bs[i].innerText.trim()=="\u67e5\u8be2"){bs[i].click();return"ok";}}return"nf";}catch(e){return"err"}})()')
print('click:',r)
time.sleep(3)
# Get full page HTML
html=js('(function(){try{var f=document.getElementById('+Q+fn+Q+');var d=f.contentDocument||f.contentWindow.document;return d.body.outerHTML.substring(0,10000);}catch(e){return"err:"+str(e)}})()')
# Find table and result rows
for line in html.split('\n'):
    l=line.strip()
    if not l:continue
    if any(k in l.lower() for k in ['table','tr','td','th','result','grid','row','cell']):
        print(l[:250])
c.close()
