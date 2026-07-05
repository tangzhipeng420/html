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

# Check navframe_def for search input
def_inputs=js('(function(){try{'+
    'var f=document.getElementById('+Q+'navframe_def'+Q+');'+
    'if(!f||!f.contentDocument)return"nf";'+
    'var d=f.contentDocument;'+
    'var es=d.querySelectorAll("input,textarea");'+
    'var r=[];'+
    'for(var i=0;i<es.length;i++){'+
        'r.push(es[i].outerHTML.substring(0,500));'+
    '}'+
    'return r.join("\\n====\\n");'+
'}catch(e){return"err"}})()')
print('=== NAVFRAME_DEF INPUTS ===')
print(def_inputs[:2000])
print()

# Also check the menu_search element for any input
search_html=js('(function(){try{'+
    'var e=document.getElementById("menu_search_ct");'+
    'return e?e.innerHTML.substring(0,2000):"nf";'+
'}catch(e){return"err"}})()')
print('=== menu_search_ct INNER HTML ===')
print(search_html)

c.close()
