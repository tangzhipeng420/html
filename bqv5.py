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

# ---- STEP 1: Navigate to equity pool page ----
lg('Loading equity pool page...')
js('(function(){try{'+
    'var w=document.getElementById("navframe_def").contentWindow;'+
    'w.$.search.gotoNav('+
        Q+'家庭抵用券（权益池）'+Q+','+
        Q+'/ordercentre/ordercentre?service=page/oc.person.cs.fusion.Equitypoolquery&listener=onInitBusi&MENU_ID=FUSE20210917'+Q+','+
        Q+Q+','+
        '{MENU_ID:'+Q+'FUSE20210917'+Q+'}'+
    ');'+
    'return"ok";'+
'}catch(e){return"err"}})()')
time.sleep(3)

# ---- STEP 2: Find equity iframe ----
eq_win=js('(function(){try{'+
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
lg(f'Equity iframe: {eq_win}')

# ---- STEP 3: Test query ----
def query_cust_billing(ph):
    """Original billing API query via navframe_133"""
    js('window.__CDP_RES__=null;')
    # Set phone in navframe_133
    js('(function(){try{'+
        'document.getElementById('+Q+'navframe_133'+Q+').contentDocument.getElementById('+Q+'ACCESS_NUMBER'+Q+').value='+Q+ph+Q+';'+
        'return"ok";}catch(e){return"err"}})()')
    time.sleep(0.3)
    # Call API
    js('(function(){try{'+
        'var w=document.getElementById('+Q+'navframe_133'+Q+').contentWindow;'+
        'w.agentUtil.ajax({'+
            'url:"AgentCentre.person.payment.IAgentPaymentSV.queryBaseInfoPayment",'+
            'refreshCust:true,'+
            'data:{ACCESS_NUMBER:'+Q+ph+Q+',REMOVE_TAG:""},'+
            'success:function(res){window.__CDP_RES__=res;}'+
        '});'+
        'return"ok";}catch(e){return"err"}})()')
    # Wait for result
    for _ in range(30):
        time.sleep(0.3)
        r=js('(function(){try{var v=window.__CDP_RES__;return v?JSON.stringify(v):null;}catch(e){return"null"}})()')
        if r and r!='null' and len(r)>10:
            try:
                data=json.loads(r).get('DATA',{})
                if not data.get('CUST_NAME'):return None
                info={}
                info['name']=(data.get('CUST_NAME','') or '')[:1]
                info['plan']=data.get('OFFER_NAME','') or ''
                info['card']=data.get('GOTONE_LEVEL_NAME','') or ''
                info['arpu_m']=str(data.get('GOTONE_MONTH_ARPU','') or '')
                info['arpu_y']=str(data.get('GOTONE_YEAR_ARPU','') or '')
                return info
            except:
                pass
    return None

def query_equity(ph, fid):
    """Query equity balance from the equity pool iframe"""
    # Set phone
    js('(function(){try{'+
        'var f=document.getElementById('+Q+fid+Q+');'+
        'var d=f.contentDocument;'+
        'd.getElementById("ACCESS_NUMBER").value='+Q+ph+Q+';'+
        'var li=d.getElementById("LOGIN_USER_ID");li.value='+Q+ph+Q+';'+
        'li.dispatchEvent(new Event("input",{bubbles:true}));'+
        'return"ok";}catch(e){return"err"}})()')
    time.sleep(0.5)
    # Call checkBaseQuery in equity iframe
    js('(function(){try{'+
        'document.getElementById('+Q+fid+Q+').contentWindow.checkBaseQuery();'+
        'return"ok";}catch(e){return"err"}})()')
    time.sleep(2)
    # Read result
    txt=js('(function(){try{'+
        'var d=document.getElementById('+Q+fid+Q+').contentDocument;'+
        'return d.body.innerText.substring(0,3000);'+
    '}catch(e){return""}})()')
    # Parse equity values
    for line in txt.split('\n'):
        s=line.strip()
        if '权益金余额' in s:
            # Look for number after "权益金余额："
            parts=s.split('：')
            if len(parts)>1:
                val=parts[-1].strip()
                return val
    return '---'

# Test
lg('Testing billing + equity...')
b=query_cust_billing('15108742724')
e=query_equity('15108742724',eq_win)
lg(f'Billing: {b}')
lg(f'Equity: {e}')

# Batch
if not os.path.exists(SR):
    lg('No file:'+SR)
    c.close()
    exit()

wb=openpyxl.load_workbook(SR)
ws=wb.active
phs=[str(ws.cell(r,1).value or'').strip() for r in range(2,ws.max_row+1) if ws.cell(r,1).value]
lg('Total:'+str(len(phs)))

out=openpyxl.Workbook()
osx=out.active
osx.append(['号码','姓','套餐','全球通卡类型','年评ARPU','月评ARPU','权益金余额'])
ok=fail=0

for idx,ph in enumerate(phs[:10]):
    lg(f'[{idx+1}] {ph}')
    try:
        b=query_cust_billing(ph)
        e=query_equity(ph,eq_win)
        if b is None:
            osx.append([ph,'','','','','',''])
            fail+=1
        else:
            osx.append([ph,b['name'],b['plan'],b['card'],b['arpu_y'],b['arpu_m'],e])
            ok+=1
    except Exception as ex:
        osx.append([ph,'','','','','',str(ex)[:80]])
        fail+=1

out.save(OU)
lg(f'{ok}ok {fail}fail saved to {OU}')
c.close()
