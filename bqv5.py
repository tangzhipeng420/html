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

lg('Step1: Restore billing page (navframe_133)...')
# Search and click billing to restore navframe_133
js('(function(){try{'+
    'var w=document.getElementById("navframe_def").contentWindow;'+
    'w.$.search.gotoNav('+
        '"代收话费",'+
        '"/agentcentre/agentcentre?service=page/oc.person.payment.customer.paymentquery&listener=init&MENU_ID=20210914",'+
        '"",'+
        '{MENU_ID:"20210914"}'+
    ');return"ok";'+
    '}catch(e){return"err"}})()')
time.sleep(3)

lg('Step2: Navigate to equity pool page...')
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
lg(f'Equity iframe: {eq_id}')

def query_billing(ph):
    """Query billing API from navframe_133"""
    js('window.__CDP_RES__=null;')
    # Set phone
    js('(function(){try{'+
        'document.getElementById("navframe_133").contentDocument.getElementById("ACCESS_NUMBER").value="'+ph+'";'+
        'return"ok";}catch(e){return"err"}})()')
    time.sleep(0.3)
    # Call API
    js('(function(){try{'+
        'var w=document.getElementById("navframe_133").contentWindow;'+
        'w.agentUtil.ajax({'+
            'url:"AgentCentre.person.payment.IAgentPaymentSV.queryBaseInfoPayment",'+
            'refreshCust:true,'+
            'data:{ACCESS_NUMBER:"'+ph+'",REMOVE_TAG:""},'+
            'success:function(r){window.__CDP_RES__=r;}'+
        '});return"ok";}catch(e){return"err"}})()')
    for _ in range(30):
        time.sleep(0.3)
        r=js('window.__CDP_RES__?JSON.stringify(window.__CDP_RES__):null')
        if r and r!='null' and len(r)>10:
            try:
                dd=json.loads(r).get('DATA',{})
                if not dd.get('CUST_NAME'):return None
                return {
                    'name':(dd.get('CUST_NAME','') or '')[:1],
                    'plan':dd.get('OFFER_NAME','') or '',
                    'card':dd.get('GOTONE_LEVEL_NAME','') or '',
                    'arpu_m':str(dd.get('GOTONE_MONTH_ARPU','') or ''),
                    'arpu_y':str(dd.get('GOTONE_YEAR_ARPU','') or ''),
                }
            except:
                pass
    return None

def query_equity(ph, fid):
    """Query equity balance"""
    js('(function(){try{'+
        'var f=document.getElementById("'+fid+'");'+
        'var d=f.contentDocument;'+
        'd.getElementById("ACCESS_NUMBER").value="'+ph+'";'+
        'var li=d.getElementById("LOGIN_USER_ID");li.value="'+ph+'";'+
        'li.dispatchEvent(new Event("input",{bubbles:true}));'+
        'return"ok";}catch(e){return"err"}})()')
    time.sleep(0.5)
    js('(function(){try{'+
        'document.getElementById("'+fid+'").contentWindow.checkBaseQuery();'+
        'return"ok";}catch(e){return"err"}})()')
    time.sleep(2)
    txt=js('document.getElementById("'+fid+'").contentDocument.body.innerText')
    for line in txt.split('\n'):
        s=line.strip()
        if '权益金余额' in s:
            parts=s.split('：')
            if len(parts)>1:
                return parts[-1].strip()
    return '---'

# Load phones
if not os.path.exists(SR):
    lg('No file:'+SR)
    c.close();exit()

wb=openpyxl.load_workbook(SR)
ws=wb.active
phs=[str(ws.cell(r,1).value or'').strip() for r in range(2,ws.max_row+1) if ws.cell(r,1).value]
lg(f'Total:{len(phs)}')

out=openpyxl.Workbook()
osx=out.active
osx.append(['号码','姓','套餐','全球通卡类型','年评ARPU','月评ARPU','权益金余额'])
ok=fail=0

for idx,ph in enumerate(phs[:10]):
    lg(f'[{idx+1}] {ph}')
    try:
        bi=query_billing(ph)
        eq=query_equity(ph,eq_id)
        if bi is None:
            osx.append([ph,'','','','','',eq])
            fail+=1
        else:
            osx.append([ph,bi['name'],bi['plan'],bi['card'],bi['arpu_y'],bi['arpu_m'],eq])
            ok+=1
    except Exception as ex:
        osx.append([ph,'','','','','',str(ex)[:80]])
        fail+=1

out.save(OU)
lg(f'{ok}ok {fail}fail')
lg(f'Saved to {OU}')
c.close()
