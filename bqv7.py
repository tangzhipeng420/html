import websocket,json,urllib.request,time,openpyxl,os
CP=19222
SR=os.path.join('C:'+os.sep,'Users','Administrator','Desktop','水池.xlsx')
OU=os.path.join('C:'+os.sep,'Users','Administrator','Desktop','水池_结果.xlsx')

def lg(m):
    t=time.strftime('%H:%M:%S')
    print(f'[{t}] {m}',flush=True)

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
            if rs.get('isException'):return ''
            return rs.get('result',{}).get('value','')

Q='"'

# Find billing iframe with ACCESS_NUMBER + payment in src
bid=js('(function(){try{var es=document.querySelectorAll("iframe");for(var i=0;i<es.length;i++){try{var d=es[i].contentDocument;if(d&&d.getElementById("ACCESS_NUMBER")&&es[i].src.indexOf("payment")>=0){return es[i].id;}}catch(e){}}return"nf";}catch(e){return"err"}})()')
lg(f'Bill iframe: {bid}')

# If no billing iframe found, navigate to billing page first
if bid=='nf':
    lg('Navigating to billing...')
    js('document.getElementById("navframe_def").contentWindow.$.search.gotoNav("代收话费","/agentcentre/agentcentre?service=page/oc.person.payment.customer.paymentquery&listener=init&MENU_ID=20210914","",{MENU_ID:"20210914"})')
    time.sleep(4)
    bid=js('(function(){try{var es=document.querySelectorAll("iframe");for(var i=0;i<es.length;i++){try{var d=es[i].contentDocument;if(d&&d.getElementById("ACCESS_NUMBER")&&es[i].src.indexOf("payment")>=0){return es[i].id;}}catch(e){}}return"nf";}catch(e){return"err"}})()')
    lg(f'Now bill iframe: {bid}')

# Load phones
wb=openpyxl.load_workbook(SR)
ws=wb.active
phs=[str(ws.cell(r,1).value or'').strip() for r in range(2,ws.max_row+1) if ws.cell(r,1).value]
lg(f'{len(phs)} phones')

out=openpyxl.Workbook()
osx=out.active
osx.append(['号码','姓','套餐','全球通卡类型','年评ARPU','月评ARPU','权益金余额'])

br={}
# Phase 1: Billing
for idx,ph in enumerate(phs[:3]):
    lg(f'B{idx+1}: {ph}')
    js('window.__CDP_RES__=null;')
    js('(function(){try{'+
        'var d=document.getElementById("'+bid+'").contentDocument;'+
        'd.getElementById("ACCESS_NUMBER").value="'+ph+'";'+
        'return"ok";}catch(e){return"err"}})()')
    time.sleep(0.3)
    # Call API from iframe's window object
    js('(function(){try{'+
        'var w=document.getElementById("'+bid+'").contentWindow;'+
        'var obj={};obj.ACCESS_NUMBER="'+ph+'";obj.REMOVE_TAG="";'+
        'w.agentUtil.ajax({'+
            'url:"AgentCentre.person.payment.IAgentPaymentSV.queryBaseInfoPayment",'+
            'refreshCust:true,'+
            'data:obj,'+
            'success:function(res){window.__CDP_RES__=res;}'+
        '});return"ok";}catch(e){return"err"}})()')
    for _ in range(20):
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
                break
            except:
                pass
    if ph not in br:
        br[ph]='|||||'

# Phase 2: Equity
lg('Phase2: Navigate to equity...')
js('document.getElementById("navframe_def").contentWindow.$.search.gotoNav("家庭抵用券（权益池）","/ordercentre/ordercentre?service=page/oc.person.cs.fusion.Equitypoolquery&listener=onInitBusi&MENU_ID=FUSE20210917","",{MENU_ID:"FUSE20210917"})')
time.sleep(3)

# Find equity iframe by LOGIN_USER_ID
eqid=js('(function(){try{var es=document.querySelectorAll("iframe");for(var i=0;i<es.length;i++){try{var d=es[i].contentDocument;if(d&&d.getElementById("LOGIN_USER_ID")&&d.getElementById("ACCESS_NUMBER")){return es[i].id;}}catch(e){}}return"nf";}catch(e){return"err"}})()')
lg(f'Eq iframe: {eqid}')

for idx,ph in enumerate(phs[:3]):
    lg(f'E{idx+1}: {ph}')
    eq='---'
    if eqid!='nf':
        try:
            js('(function(){try{'+
                'var d=document.getElementById("'+eqid+'").contentDocument;'+
                'd.getElementById("ACCESS_NUMBER").value="'+ph+'";'+
                'd.getElementById("LOGIN_USER_ID").value="'+ph+'";'+
                'd.getElementById("LOGIN_USER_ID").dispatchEvent(new Event("input",{bubbles:true}));'+
                'return"ok";}catch(e){return"err"}})()')
            time.sleep(0.5)
            js('document.getElementById("'+eqid+'").contentWindow.checkBaseQuery()')
            time.sleep(2)
            txt=js('document.getElementById("'+eqid+'").contentDocument.body.innerText')
            for line in txt.split('\n'):
                s=line.strip()
                if '权益池额度' in s or '权益金余额' in s:
                    p=s.split('：')
                    if len(p)>1:eq=p[-1].strip();break
        except Exception as ex:
            eq=str(ex)[:30]
    # Build row
    bi=br.get(ph,'|||||')
    row=[ph]+bi.split('|')+[eq]
    osx.append(row)

out.save(OU)
lg('Done')
c.close()
