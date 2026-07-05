# -*- coding: utf-8 -*-
import websocket,json,urllib.request,time

p=json.loads(urllib.request.urlopen('http://[::1]:19222/json',timeout=3).read())
c=websocket.create_connection('ws://[::1]:19222/devtools/page/'+p[0]['id'],timeout=5)
c.settimeout(10)
n=0
def js(e):
    global n;n+=1
    c.send(json.dumps({'id':n,'method':'Runtime.evaluate','params':{'expression':e,'returnByValue':True}}))
    while 1:
        r=json.loads(c.recv())
        if r.get('id')==n:
            rs=r.get('result',{})
            if rs.get('isException'):return'__EXC__'
            return rs.get('result',{}).get('value','')

# Check if search function exists
r=js('typeof document.getElementById("navframe_def").contentWindow.$')
print('$:',r,flush=True)
r=js('typeof document.getElementById("navframe_def").contentWindow.$.search')
print('$.search:',r,flush=True)

# Try to search menu items
r=js("(function(){try{var w=document.getElementById('navframe_def').contentWindow;var m=w.$('#menu_search');return m.length>0?'search_found':'search_nf';}catch(e){return'ERR';}})()")
print('Menu search:',r,flush=True)

# Look at all navframe_xx titles
r=js("(function(){var es=document.querySelectorAll('iframe');var out=[];for(var i=0;i<es.length;i++){try{var d=es[i].contentDocument;out.push(es[i].id+'='+(d?d.title:'-'));}catch(e){out.push(es[i].id+'=ERR')}}return out.join('|');})()")
print('Titles:',r,flush=True)

# Find 代收话费 menu item if available
r=js("(function(){try{var w=document.getElementById('navframe_def').contentWindow;var items=w.$('#menu_ul li');var out=[];for(var i=0;i<items.length;i++){var t=items[i].textContent||'';out.push(t.substring(0,30));}return out.join('||');}catch(e){return'ERR:'+e.message.substring(0,50)}})()")
print('Menu items:',r,flush=True)

c.close()
