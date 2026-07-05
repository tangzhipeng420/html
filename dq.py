# -*- coding: utf-8 -*-
# Simple: equity only, unique iframe ids
import websocket,json,urllib.request,time,openpyxl,os,sys
CP=19222
SR=os.path.join('C:'+os.sep,'Users','Administrator','Desktop','水池.xlsx')
OU=os.path.join('C:'+os.sep,'Users','Administrator','Desktop','水池_结果.xlsx')

import time as t
uid=str(t.time()).replace('.','')
lg=lambda m:print(t.strftime('%H:%M:%S'),m,flush=True)

# CDP
try:
    p=json.loads(urllib.request.urlopen(f'http://[::1]:{CP}/json',timeout=3).read())
    c=websocket.create_connection(f'ws://[::1]:{CP}/devtools/page/'+p[0]['id'],timeout=5)
except Exception as ex:
    lg('CDP FAIL:'+str(ex))
    exit()

n=0
def js(cd):
    global n
    n+=1
    c.send(json.dumps({'id':n,'method':'Runtime.evaluate','params':{'expression':cd,'returnByValue':True}}))
    c.settimeout(5)
    try:
        while True:
            r=json.loads(c.recv())
            if r.get('id')==n:
                rs=r.get('result',{});
                if rs.get('isException'):return''
                return rs.get('result',{}).get('value','')
    except:
        return ''

# Clean old iframes
js("['ef','bf','eqp','eqFrame'].forEach(function(x){try{var f=document.getElementById(x);if(f)f.parentNode.removeChild(f);}catch(e){}})")
t.sleep(1)

# Load phones
ph=openpyxl.load_workbook(SR).active
phs=[str(ph.cell(r,1).value or'').strip() for r in range(2,ph.max_row+1) if ph.cell(r,1).value]
lg('Phones:'+str(len(phs)))

# Skip if result exists and has data
st=0
if os.path.exists(OU):
    try:
        wb2=openpyxl.load_workbook(OU)
        st=wb2.active.max_row
    except:
        st=0
phs=phs[st:st+5]
if not phs:lg('All done');exit()

wb2=openpyxl.Workbook() if st==0 else openpyxl.load_workbook(OU)
osx=wb2.active
if st==0:
    osx.append(['号码','权益金余额'])

# Create equity iframe
eqid='eq_'+uid
js("(function(){var f=document.createElement('iframe');f.id='"+eqid+"';f.style.display='none';f.src='/ordercentre/ordercentre?service=page/oc.person.cs.fusion.Equitypoolquery&listener=onInitBusi&MENU_ID=FUSE20210917';document.body.appendChild(f);return'ok';})()")
t.sleep(5)

for idx,ph in enumerate(phs):
    eq='---'
    try:
        js("document.getElementById('"+eqid+"').contentDocument.getElementById('ACCESS_NUMBER').value='"+ph+"'")
        js("document.getElementById('"+eqid+"').contentDocument.getElementById('LOGIN_USER_ID').value='"+ph+"'")
        js("document.getElementById('"+eqid+"').contentDocument.getElementById('LOGIN_USER_ID').dispatchEvent(new Event('input',{bubbles:true}))")
        t.sleep(1)
        js("document.getElementById('"+eqid+"').contentWindow.checkBaseQuery()")
        t.sleep(3)
        txt=js("document.getElementById('"+eqid+"').contentDocument.body.innerText")
        for line in txt.split('\n'):
            s=line.strip()
            if '\u6743\u76ca\u6c60\u989d' in s or '\u6743\u76ca\u91d1' in s:
                p=s.split('\uff1a')
                if len(p)>1:
                    eq=p[-1].strip()
                    break
    except:
        eq='err'
    osx.append([ph,eq])
    try:wb2.save(OU)
    except:pass
    lg(f'{ph}:{eq}')

try:wb2.save(OU)
except:pass
lg('Done:'+str(len(phs)))
c.close()
