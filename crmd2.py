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

# List ALL iframes after page load
def list_iframes():
    return js('(function(){try{var fs=document.querySelectorAll("iframe");var r=[];for(var i=0;i<fs.length;i++){r.push(fs[i].id||"no-id-"+i+":src="+(fs[i].src||"").substring(0,100));}return r.join(chr(10));}catch(e){return"err:"+str(e)}})()')

print("=== ALL IFRAMES before query ===")
print(list_iframes())

# Now query a number via navframe_133
fn='navframe_133'
ph='15108742724'
r=js('(function(){try{var f=document.getElementById('+Q+fn+Q+');var d=f.contentDocument||f.contentWindow.document;d.getElementById('+Q+'ACCESS_NUMBER'+Q+').value='+Q+ph+Q+';return"ok";}catch(e){return"err"}})()')
time.sleep(0.5)
r=js('(function(){try{var f=document.getElementById('+Q+fn+Q+');var d=f.contentDocument||f.contentWindow.document;var bs=d.querySelectorAll("button");for(var i=0;i<bs.length;i++){if(bs[i].innerText.trim()=="\u67e5\u8be2"){bs[i].click();return"ok";}}return"nf";}catch(e){return"err"}})()')
print('click query btn:',r)
time.sleep(3)

# Check if new iframes appeared or page changed
print("\n=== ALL IFRAMES after query ===")
print(list_iframes())

# Check CDP targets (new tabs/pages)
print("\n=== CDP TARGETS ===")
targets=json.loads(urllib.request.urlopen(f'http://[::1]:{CP}/json',timeout=3).read())
for t in targets:
    print(f"  {t.get('id','')[:20]}... type={t.get('type','')} title={t.get('title','')[:50]} url={t.get('url','')[:80]}")

# Check each iframe body
for fid in ['navframe_133','navframe_161','navframe_def','leidaFrame','drawerIframe']:
    txt=js('(function(){try{var f=document.getElementById('+Q+fid+Q+');if(!f||!f.contentDocument)return"nf";var d=f.contentDocument||f.contentWindow.document;return(d.body.innerText||"").substring(0,500);}catch(e){return"err"}})()')
    print(f"\n=== {fid} ===")
    for line in txt.split('\n'):
        if line.strip():
            print(line.strip()[:150])

c.close()
