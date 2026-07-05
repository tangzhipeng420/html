# -*- coding: utf-8 -*-
import websocket,json,urllib.request,time,openpyxl,os,sys
CP=19222
SR=os.path.join('C:'+os.sep,'Users','Administrator','Desktop','水池.xlsx')
OU=os.path.join('C:'+os.sep,'Users','Administrator','Desktop','水池_结果.xlsx')
START=0
N=3

def lg(m):
    t=time.strftime('%H:%M:%S')
    print(f'[{t}] {m}',flush=True)

# Connect CDP
lg('Connecting CDP...')
try:
    p=json.loads(urllib.request.urlopen(f'http://[::1]:{CP}/json',timeout=3).read())
    c=websocket.create_connection(f'ws://[::1]:{CP}/devtools/page/'+p[0]['id'],timeout=5)
except Exception as ex:
    lg(f'CDP FAIL: {ex}')
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
                rs=r.get('result',{})
                if rs.get('isException'):return''
                return rs.get('result',{}).get('value','')
    except:
        return ''

# Load phones
wb=openpyxl.load_workbook(SR)
ws=wb.active
all_phones=[str(ws.cell(r,1).value or'').strip() for r in range(2,ws.max_row+1) if ws.cell(r,1).value]
phs=all_phones[START:START+N]
lg(f'{len(all_phones)} phones total, batch {START+1}-{START+len(phs)}')

# Try to use existing result file
if os.path.exists(OU):
    wb2=openpyxl.load_workbook(OU)
    osx=wb2.active
else:
    wb2=openpyxl.Workbook()
    osx=wb2.active
    osx.append(['号码','姓','套餐','全球通卡','年评ARPU','月评ARPU','权益金余额'])

# Phase 1: Try billing if already open
bid=js("(function(){try{var es=document.querySelectorAll('iframe');for(var i=0;i<es.length;i++){try{var d=es[i].contentDocument;if(d&&d.getElementById('ACCESS_NUMBER')&&d.defaultView&&d.defaultView.agentUtil){return es[i].id;}}catch(e){}}}return'nf';})()")
lg(f'Billing iframe: {bid}')

br={}
if bid!='nf':
    for idx,ph in enumerate(phs):
        lg(f'B{idx+1}: {ph}')
        js('window.__CDP_RES__=null;')
        js("document.getElementById('"+bid+"').contentDocument.getElementById('ACCESS_NUMBER').value='"+ph+"'")
        time.sleep(0.3)
        js("(function(){try{var w=document.getElementById('"+bid+"').contentWindow;var o={ACCESS_NUMBER:'"+ph+"',REMOVE_TAG:''};w.agentUtil.ajax({url:'AgentCentre.person.payment.IAgentPaymentSV.queryBaseInfoPayment',refreshCust:true,data:o,success:function(rr){window.__CDP_RES__=rr;}});return'ok';}catch(e){return'err'}})()")
        got=False
        for _ in range(15):
            time.sleep(0.3)
            r=js('window.__CDP_RES__?JSON.stringify(window.__CDP_RES__):null')
            if r and r!='null' and len(r)>20:
                try:
                    dd=json.loads(r).get('DATA',{})
                    nm=dd.get('CUST_NAME','')
                    if nm:
                        br[ph]=f'{nm[:1]}|{dd.get("OFFER_NAME","")}|{dd.get("GOTONE_LEVEL_NAME","")}|{dd.get("GOTONE_YEAR_ARPU","")}|{dd.get("GOTONE_MONTH_ARPU","")}'
                    else:
                        br[ph]='|不存在|||'
                    got=True;break
                except:pass
        if not got:
            br[ph]='|||||'
            lg(f'  Billing timeout')
else:
    lg('No billing page open. Run billing phase after clicking "代收话费".')
    for ph in phs:
        br[ph]='|||||'

# Phase 2: Equity
lg('Loading equity pool...')
js("(function(){var f=document.createElement('iframe');f.id='ef';f.style.display='none';f.src='/ordercentre/ordercentre?service=page/oc.person.cs.fusion.Equitypoolquery&listener=onInitBusi&MENU_ID=FUSE20210917';document.body.appendChild(f);return'ok';})()")
time.sleep(5)

eqid=js("(function(){try{var f=document.getElementById('ef');if(f){try{var d=f.contentDocument;if(d&&d.getElementById('LOGIN_USER_ID')){return'ef';}}catch(e){}}return'nf';}catch(e){return'err'}})()")
lg(f'Equity iframe: {eqid}')

for idx,ph in enumerate(phs):
    lg(f'E{idx+1}: {ph}')
    eq='---'
    if eqid not in ('nf','err',''):
        try:
            js("document.getElementById('"+eqid+"').contentDocument.getElementById('ACCESS_NUMBER').value='"+ph+"'")
            js("document.getElementById('"+eqid+"').contentDocument.getElementById('LOGIN_USER_ID').value='"+ph+"'")
            js("document.getElementById('"+eqid+"').contentDocument.getElementById('LOGIN_USER_ID').dispatchEvent(new Event('input',{bubbles:true}))")
            time.sleep(1)
            js("document.getElementById('"+eqid+"').contentWindow.checkBaseQuery()")
            time.sleep(3)
            txt=js("document.getElementById('"+eqid+"').contentDocument.body.innerText")
            for line in txt.split('\n'):
                s=line.strip()
                if '\u6743\u76ca\u6c60\u989d' in s or '\u6743\u76ca\u91d1' in s:
                    p=s.split('\uff1a')
                    if len(p)>1:eq=p[-1].strip();break
        except:
            eq='err'
    bi=br.get(ph,'|||||')
    osx.append([ph]+bi.split('|')+[eq])
    # Save after each number
    try: wb2.save(OU)
    except: pass

try: wb2.save(OU)
except: pass
lg(f'Done! {len(phs)} phones done, saved to {OU}')
c.close()
