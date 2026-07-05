import websocket,json,urllib.request,time,openpyxl,os,sys
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
            if rs.get('isException'):return''
            return rs.get('result',{}).get('value','')

Q='"'

# Phase 1: Query billing info for ALL numbers
lg('Phase1: Load billing page...')
js('(function(){try{'+
    'var w=document.getElementById("navframe_def").contentWindow;'+
    'w.$.search.gotoNav('+
        Q+'代收话费'+Q+','+
        Q+'/agentcentre/agentcentre?service=page/oc.person.payment.customer.paymentquery&listener=init&MENU_ID=20210914'+Q+','+
        Q+Q+','+
        '{MENU_ID:'+Q+'20210914'+Q+'}'+
    ');return"ok";'+
'}catch(e){return"err"}})()')
time.sleep(3)

def q_billing(ph):
    js('window.__CDP_RES__=null;')
    js('(function(){try{'+
        'document.getElementById("navframe_133").contentDocument.getElementById("ACCESS_NUMBER").value="'+ph+'";'+
        'return"ok";}catch(e){return"err"}})()')
    time.sleep(0.3)
    js('(function(){try{'+
        'var w=document.getElementById("navframe_133").contentWindow;'+
        'w.agentUtil.ajax({'+
            'url:"AgentCentre.person.payment.IAgentPaymentSV.queryBaseInfoPayment",'+
            'refreshCust:true,'+
            'data:{ACCESS_NUMBER:"'+ph+'",REMOVE_TAG:""},'+
            'success:function(r){window.__CDP_RES__=r;}'+
        '});return"ok";}catch(e){return"err"}})()')
    for _ in range(20):
        time.sleep(0.3)
        r=js('window.__CDP_RES__?JSON.stringify(window.__CDP_RES__):null')
        if r and r!='null' and len(r)>20:
            try:
                dd=json.loads(r).get('DATA',{})
                if not dd.get('CUST_NAME'):return None
                return f'{dd.get("CUST_NAME","")[:1]}|{dd.get("OFFER_NAME","")}|{dd.get("GOTONE_LEVEL_NAME","")}|{dd.get("GOTONE_YEAR_ARPU","")}|{dd.get("GOTONE_MONTH_ARPU","")}'
            except:
                pass
    return None

# Load phones
wb=openpyxl.load_workbook(SR)
ws=wb.active
phs=[str(ws.cell(r,1).value or'').strip() for r in range(2,ws.max_row+1) if ws.cell(r,1).value]
lg(f'Total:{len(phs)}, batch=10')

out=openpyxl.Workbook()
osx=out.active
osx.append(['号码','姓','套餐','全球通卡类型','年评ARPU','月评ARPU','权益金余额'])
ok=fail=0

# Phase1: Billing for first 10
results={}
for idx,ph in enumerate(phs[:10]):
    lg(f'Billing [{idx+1}] {ph}')
    bi=q_billing(ph)
    if bi:results[ph]=bi+'|'
    else:results[ph]='|||||'
    ok+=1

# Phase2: Equity page
lg('Phase2: Load equity page...')
js('(function(){try{'+
    'var w=document.getElementById("navframe_def").contentWindow;'+
    'w.$.search.gotoNav('+
        Q+'家庭抵用券（权益池）'+Q+','+
        Q+'/ordercentre/ordercentre?service=page/oc.person.cs.fusion.Equitypoolquery&listener=onInitBusi&MENU_ID=FUSE20210917'+Q+','+
        Q+Q+','+
        '{MENU_ID:'+Q+'FUSE20210917'+Q+'}'+
    ');return"ok";'+
'}catch(e){return"err"}})()')
time.sleep(3)

# Find equity iframe
eq_id=js('(function(){try{'+
    'var es=document.querySelectorAll("iframe");'+
    'for(var i=0;i<es.length;i++){'+
        'try{'+
            'var d=es[i].contentDocument;'+
            'if(d&&d.getElementById("ACCESS_NUMBER")&&d.getElementById("LOGIN_USER_ID")){'+
                'return es[i].id;'+
            '}'+
        '}catch(e){}'+
    '}'+
    'return"nf";'+
'}catch(e){return"err"}})()')
lg(f'Equity iframe:{eq_id}')

for idx,ph in enumerate(phs[:10]):
    lg(f'Equity [{idx+1}] {ph}')
    try:
        js('(function(){try{'+
            'var f=document.getElementById("'+eq_id+'");'+
            'var d=f.contentDocument;'+
            'd.getElementById("ACCESS_NUMBER").value="'+ph+'";'+
            'var li=d.getElementById("LOGIN_USER_ID");li.value="'+ph+'";'+
            'li.dispatchEvent(new Event("input",{bubbles:true}));'+
            'return"ok";}catch(e){return"err"}})()')
        time.sleep(0.5)
        js('(function(){try{'+
            'document.getElementById("'+eq_id+'").contentWindow.checkBaseQuery();'+
            'return"ok";}catch(e){return"err"}})()')
        time.sleep(2)
        txt=js('document.getElementById("'+eq_id+'").contentDocument.body.innerText')
        eq_val='---'
        for line in txt.split('\n'):
            s=line.strip()
            if '权益金余额' in s:
                p=s.split('：')
                if len(p)>1:eq_val=p[-1].strip();break
        # Combine with billing result
        bi=results.get(ph,'|||||')
        parts=bi.split('|')
        row=[ph]+parts+[eq_val]
        osx.append(row)
    except Exception as ex:
        bi=results.get(ph,'|||||')
        osx.append([ph]+bi.split('|')+[str(ex)[:50]])

out.save(OU)
lg(f'Saved to {OU}')
c.close()
