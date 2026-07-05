# -*- coding: utf-8 -*-
import websocket,json,urllib.request,time,openpyxl,os
CP=19222
SR=os.path.join('C:'+os.sep,'Users','Administrator','Desktop','水池.xlsx')
OU=os.path.join('C:'+os.sep,'Users','Administrator','Desktop','水池_结果.xlsx')

def lg(m):
    print(f'[{time.strftime("%H:%M:%S")}] {m}',flush=True)

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

# Find billing iframe - one with ACCESS_NUMBER but NO LOGIN_USER_ID
bid=js('(function(){try{var es=document.querySelectorAll("iframe");for(var i=0;i<es.length;i++){try{var d=es[i].contentDocument;if(d&&d.getElementById("ACCESS_NUMBER")&&!d.getElementById("LOGIN_USER_ID")){return es[i].id;}}catch(e){}}return"nf";}catch(e){return"err"}})()')
lg(f'Bill iframe: {bid}')
if bid=='nf':
    lg('ERROR: No billing iframe found. Click "代收话费" in CRM first!')
    c.close();exit()

wb=openpyxl.load_workbook(SR)
ws=wb.active
phs=[str(ws.cell(r,1).value or'').strip() for r in range(2,ws.max_row+1) if ws.cell(r,1).value]
lg(f'{len(phs)} phones')

out=openpyxl.Workbook()
osx=out.active
osx.append(['号码','姓','套餐','全球通卡类型','年评ARPU','月评ARPU'])

for idx,ph in enumerate(phs[:3]):
    lg(f'#{idx+1}: {ph}')
    js('window.__CDP_RES__=null;')
    # Set phone number
    js('(function(){try{'+
        'document.getElementById("'+bid+'").contentDocument.getElementById("ACCESS_NUMBER").value="'+ph+'";'+
        'return"ok";}catch(e){return"err"}})()')
    time.sleep(0.3)
    # Call billing API from iframe
    js('(function(){try{'+
        'var w=document.getElementById("'+bid+'").contentWindow;'+
        'var o={};o.ACCESS_NUMBER="'+ph+'";o.REMOVE_TAG="";'+
        'w.agentUtil.ajax({url:"AgentCentre.person.payment.IAgentPaymentSV.queryBaseInfoPayment",refreshCust:true,data:o,success:function(rr){window.__CDP_RES__=rr;}});'+
        'return"ok";}catch(e){return"err"}})()')
    got=False
    for _ in range(20):
        time.sleep(0.3)
        r=js('window.__CDP_RES__?JSON.stringify(window.__CDP_RES__):null')
        if r and r!='null' and len(r)>20:
            try:
                dd=json.loads(r).get('DATA',{})
                nm=dd.get('CUST_NAME','')
                if nm:
                    osx.append([ph,nm[:1],dd.get('OFFER_NAME',''),dd.get('GOTONE_LEVEL_NAME',''),dd.get('GOTONE_YEAR_ARPU',''),dd.get('GOTONE_MONTH_ARPU','')])
                else:
                    osx.append([ph,'','不存在','','',''])
                got=True;break
            except:pass
    if not got:osx.append([ph,'','超时','','',''])

out.save(OU)
lg(f'Done -> {OU}')
c.close()
