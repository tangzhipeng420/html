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

# First, type number and let user see basic info
fn='navframe_133'
ph='15108742724'
r=js('(function(){try{var f=document.getElementById('+Q+fn+Q+');var d=f.contentDocument||f.contentWindow.document;d.getElementById('+Q+'ACCESS_NUMBER'+Q+').value='+Q+ph+Q+';return"ok";}catch(e){return"err"}})()')
time.sleep(0.5)

# Instead of clicking "查询" button, let's check what JS functions are available
# Look at the window scope
funcs=js('(function(){try{var f=document.getElementById('+Q+fn+Q+');var d=f.contentDocument||f.contentWindow.document;var w=d.defaultView||d.parentWindow;var k=Object.keys(w);var r=[];for(var i=0;i<k.length;i++){try{if(typeof w[k[i]]==="function"&&k[i].toLowerCase().indexOf("query")>=0)r.push(k[i]);}catch(e){}}return r.join("|");}catch(e){return"err"}})()')
print('=== QUERY-RELATED FUNCTIONS ===')
for fn_name in funcs.split('|'):
    if fn_name.strip():
        print(fn_name)

# Check the AJAX calls / network requests
# Look at the source of checkBaseQuery
src=js('(function(){try{var f=document.getElementById('+Q+'navframe_133'+Q+');var d=f.contentDocument||f.contentWindow.document;return String(d.getElementById("checkBaseQueryBtn").onclick);}catch(e){return"err"}})()')
print('\n=== checkBaseQueryBtn onclick ===')
print(src[:2000])

# Look for any API endpoints in scripts
scripts=js('(function(){try{var f=document.getElementById('+Q+fn+Q+');var d=f.contentDocument||f.contentWindow.document;var ss=d.querySelectorAll("script");var r=[];for(var i=0;i<ss.length;i++){var t=(ss[i].innerText||"").substring(0,200);if(t.indexOf("query")>=0||t.indexOf("ajax")>=0||t.indexOf("api")>=0)r.push(t);}return r.join("====").substring(0,5000);}catch(e){return"err"}})()')
print('\n=== RELEVANT SCRIPTS ===')
for script in scripts.split('===='):
    if script.strip():
        print(script[:300])
        print()

# Check what URL the page loads for results (XHR requests)
# Let's just try to access a customer profile URL
urls=js('(function(){try{var f=document.getElementById('+Q+fn+Q+');var d=f.contentDocument||f.contentWindow.document;var base=d.querySelector("base");return base?base.href:"";}catch(e){return""}})()')
print('=== BASE URL ===')
print(urls)

c.close()
