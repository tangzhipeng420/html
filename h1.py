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

# Check navframe_def
def_html=js('(function(){try{'+
    'var f=document.getElementById('+Q+'navframe_def'+Q+');'+
    'if(!f||!f.contentDocument)return"nf";'+
    'var d=f.contentDocument;'+
    'var es=d.querySelectorAll("input,textarea");'+
    'var r=[];'+
    'for(var i=0;i<es.length;i++){'+
        'r.push(es[i].outerHTML.substring(0,500));'+
    '}'+
    'return r.join("\\n===\\n");'+
'}catch(e){return"err"}})()')
print('INPUTS in navframe_def:')
print(def_html[:2000])

# Find home/首页 element
home=js('(function(){try{'+
    'var f=document.getElementById('+Q+'navframe_def'+Q+');'+
    'if(!f||!f.contentDocument)return"nf";'+
    'var d=f.contentDocument;'+
    'var es=d.querySelectorAll("*");'+
    'var r=[];'+
    'for(var i=0;i<es.length;i++){'+
        'var t=(es[i].innerText||"").trim();'+
        'if(t=="首页"){'+
            'r.push(es[i].outerHTML.substring(0,500));'+
        '}'+
    '}'+
    'return r.join("\\n===\\n");'+
'}catch(e){return"err"}})()')
print('\nHOME elements in navframe_def:')
print(home[:2000])

c.close()
