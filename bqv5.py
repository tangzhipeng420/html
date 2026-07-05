# -*- coding: utf-8 -*-
import websocket,json,urllib.request,time,openpyxl,os
CP=19222
SR=os.path.join('C:'+os.sep,'Users','Administrator','Desktop','水池.xlsx')
OU=os.path.join('C:'+os.sep,'Users','Administrator','Desktop','水池_结果.xlsx')

def lg(m):
    t=time.strftime('%H:%M:%S')
    print(f'[{t}] {m}',flush=True)

try:
    p=json.loads(urllib.request.urlopen(f'http://[::1]:{CP}/json',timeout=3).read())
    c=websocket.create_connection(f'ws://[::1]:{CP}/devtools/page/'+p[0]['id'],timeout=5)
    lg('CDP OK')
except Exception as ex:
    lg(f'CDP FAIL: {ex}')
    exit()

n=1
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
phs=[str(ws.cell(r,1).value or'').strip() for r in range(2,ws.max_row+1) if ws.cell(r,1).value]
lg(f'{len(phs)} phones')

out=openpyxl.Workbook()
osx=out.active
osx.append(['号码','姓','套餐','全球通卡类型','年评ARPU','月评ARPU','权益金余额'])

br={}

# Find billing iframe
for attempt in range(3):
    bid=js('(function(){try{var es=document.querySelectorAll("iframe");for(var i=0;i<es.length;i++){try{var d=es[i].contentDocument;if(d&&d.getElementById("ACCESS_NUMBER")){return es[i].id;}}catch(e){}}return"nf";}catch(e){return"err"}})()')
    if bid not in ('nf','err'):
        break
    lg(f'Searching iframes attempt {attempt+1}...')
    time.sleep(1)

lg(f'Billing iframe: {bid}')
if bid in ('nf','err'):
    lg('ERROR: No iframe with ACCESS_NUMBER found! Open CRM page first.')
    exit()

# Phase1: Billing for 3 numbers
for idx,ph in enumerate(phs[:3]):
    lg(f'B{idx+1}: {ph}')
    js('window.__CDP_RES__=null;')
    js('(function(){try{'+
        'document.getElementById("'+bid+'").contentDocument.getElementById("ACCESS_NUMBER").value="'+ph+'";'+
        'return"ok";}catch(e){return"err"}})()')
    time.sleep(0.3)
    js('(function(){try{'+
        'var w=document.getElementById("'+bid+'").contentWindow;'+
        'var o={};o.ACCESS_NUMBER="'+ph+'";o.REMOVE_TAG="";'+
        'w.agentUtil.ajax({url:"AgentCentre.person.payment.IAgentPaymentSV.queryBaseInfoPayment",refreshCust:true,data:o,success:function(rr){window.__CDP_RES__=rr;}});'+
        'return"ok";}catch(e){return"err"}})()')
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
        lg(f'  Billing timeout for {ph}')

# Phase2: Equity - inject iframe
lg('Phase2: Create equity iframe...')
js('(function(){try{var f=document.createElement("iframe");f.id="eqp";f.style.display="none";f.src="/ordercentre/ordercentre?service=page/oc.person.cs.fusion.Equitypoolquery&listener=onInitBusi&MENU_ID=FUSE20210917";document.body.appendChild(f);return"ok";}catch(e){return"err"}})()')
time.sleep(5)

eqid=js('(function(){try{var f=document.getElementById("eqp");if(f){try{var d=f.contentDocument;if(d&&d.getElementById("LOGIN_USER_ID")){return"eqp";}}catch(e){}}return"nf";}catch(e){return"err"}})()')

# Fallback: find any equity iframe
if eqid=='nf':
    eqid=js('(function(){try{var es=document.querySelectorAll("iframe");for(var i=0;i<es.length;i++){try{var d=es[i].contentDocument;if(d&&d.getElementById("LOGIN_USER_ID")&&d.getElementById("ACCESS_NUMBER")){return es[i].id;}}catch(e){}}return"nf";}catch(e){return"err"}})()')

lg(f'Equity iframe: {eqid}')

for idx,ph in enumerate(phs[:3]):
    lg(f'E{idx+1}: {ph}')
    eq='---'
    if eqid!='nf' and eqid!='err':
        try:
            js('(function(){try{'+
                'var d=document.getElementById("'+eqid+'").contentDocument;'+
                'd.getElementById("ACCESS_NUMBER").value="'+ph+'";'+
                'd.getElementById("LOGIN_USER_ID").value="'+ph+'";'+
                'd.getElementById("LOGIN_USER_ID").dispatchEvent(new Event("input",{bubbles:true}));'+
                'return"ok";}catch(e){return"err"}})()')
            time.sleep(1)
            js('document.getElementById("'+eqid+'").contentWindow.checkBaseQuery()')
            time.sleep(3)
            txt=js('document.getElementById("'+eqid+'").contentDocument.body.innerText')
            for line in txt.split('\n'):
                s=line.strip()
                if '\u6743\u76ca\u6c60\u989d' in s or '\u6743\u76ca\u91d1' in s:
                    p=s.split('\uff1a')
                    if len(p)>1:eq=p[-1].strip();break
        except Exception as ex:
            eq=str(ex)[:30]
    bi=br.get(ph,'|||||')
    osx.append([ph]+bi.split('|')+[eq])

out.save(OU)
lg('Done! Check 水池_结果.xlsx')
c.close()
