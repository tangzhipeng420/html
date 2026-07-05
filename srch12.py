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

# First, let's try to find the search bar by looking at the sidebar
# Send Input.dispatchKeyEvent to simulate typing
n+=1
c.send(json.dumps({'id':n,'method':'Input.dispatchKeyEvent','params':{'type':'keyDown','windowsVirtualKeyCode':84,'key':'t'}}))
r=json.loads(c.recv())
while r.get('id')!=n:r=json.loads(c.recv())

n+=1
c.send(json.dumps({'id':n,'method':'Input.dispatchKeyEvent','params':{'type':'char','text':'t','unmodifiedText':'t'}}))
r=json.loads(c.recv())
while r.get('id')!=n:r=json.loads(c.recv())

# Check if search list appeared
lst=js('(function(){try{'+
    'var u=document.getElementById("menu_search_list");'+
    'return u?u.innerHTML.substring(0,1000):"nf";'+
'}catch(e){return"err"}})()')
print('=== SEARCH LIST after "t" ===')
print(lst)

# Also check if a search input appeared
srch_input=js('(function(){try{'+
    'var es=document.querySelectorAll("input,textarea");'+
    'var r=[];'+
    'for(var i=0;i<es.length;i++){'+
        'var e=es[i];'+
        'var st=e.style;'+
        'if(st.display!="none"&&st.visibility!="hidden"&&e.type!="hidden"){'+
            'r.push(e.outerHTML.substring(0,300));'+
        '}'+
    '}'+
    'return r.join("\\n");'+
'}catch(e){return"err"}})()')
print('\n=== VISIBLE INPUTS ===')
print(srch_input)

c.close()
