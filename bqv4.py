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

def query_cust(ph):
    """Call CRM API to get customer info. Returns dict"""
    global n
    # Reset result holder
    js('(function(){try{window.__CDP_RES__=null;return\"ok\";}catch(e){return\"err\"}})()')
    n+=1
    
    # Type phone first
    js('(function(){try{'+
        'var f=document.getElementById('+Q+'navframe_133'+Q+');'+
        'var d=f.contentDocument||f.contentWindow.document;'+
        'var e=d.getElementById('+Q+'ACCESS_NUMBER'+Q+');'+
        'e.value='+Q+ph+Q+';'+
        'return\"ok\";}catch(e){return\"err\"}})()')
    n+=1
    
    # Call the AJAX API
    js('(function(){try{'+
        'var f=document.getElementById('+Q+'navframe_133'+Q+');'+
        'var w=f.contentWindow;'+
        'var obj={};'+
        'obj.ACCESS_NUMBER='+Q+ph+Q+';'+
        'obj.REMOVE_TAG="";'+
        'w.agentUtil.ajax({'+
            'url:"AgentCentre.person.payment.IAgentPaymentSV.queryBaseInfoPayment",'+
            'refreshCust:true,'+
            'data:obj,'+
            'success:function(res){'+
                'window.__CDP_RES__=res;'+
            '}'+
        '});'+
        'return\"ok\";}catch(e){return\"err\"}})()')
    n+=1
    
    # Poll for result
    for _ in range(20):
        time.sleep(0.5)
        r=js('(function(){try{var v=window.__CDP_RES__;return v?JSON.stringify(v):null;}catch(e){return\"err\"}})()')
        n+=1
        if r and r!='null' and r!='err':
            try:
                data=json.loads(r).get('DATA',{})
                info={}
                info['name']=(data.get('CUST_NAME','') or '')[:1]
                info['plan']=data.get('OFFER_NAME','') or ''
                info['card']=data.get('GOTONE_LEVEL_NAME','') or ''
                info['arpu_m']=str(data.get('GOTONE_MONTH_ARPU','') or '')
                info['arpu_y']=str(data.get('GOTONE_YEAR_ARPU','') or '')
                info['phone']=data.get('ACCESS_NUMBER','') or ''
                # Check if number exists
                if not data.get('CUST_NAME'):
                    return None
                return info
            except:
                pass
        time.sleep(0.5)
    return None

# Self-test
lg('Testing...')
r=query_cust('15108742724')
lg('R:'+str(r))
if not r:
    lg('FAIL')
    c.close()
    exit()

# Batch
if not os.path.exists(SR):
    lg('nofile:'+SR)
    c.close()
    exit()

wb=openpyxl.load_workbook(SR)
ws=wb.active
phs=[str(ws.cell(r,1).value or'').strip() for r in range(2,ws.max_row+1) if ws.cell(r,1).value and str(ws.cell(r,1).value).strip()]
lg('total:'+str(len(phs)))

out=openpyxl.Workbook()
osx=out.active
osx.append(['号码','姓','套餐','全球通卡类型','年评ARPU','月评ARPU'])
ok=fail=0

for idx,ph in enumerate(phs[:3]):
    lg(f'[{ok+fail+1}] {ph}')
    try:
        info=query_cust(ph)
        if info is None:
            osx.append([ph,'','','','','','不存在'])
            fail+=1
        else:
            osx.append([ph,info['name'],info['plan'],info['card'],info['arpu_y'],info['arpu_m']])
            ok+=1
    except Exception as e:
        osx.append([ph,'','','','','',str(e)[:100]])
        fail+=1

out.save(OU)
lg(str(ok)+'ok '+str(fail)+'fail')
c.close()
