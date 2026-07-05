# -*- coding: utf-8 -*-
import websocket,json,urllib.request,time,openpyxl,os
CP=19222;SR=os.path.join('C:'+os.sep,'Users','Administrator','Desktop','水池.xlsx')
OU=os.path.join('C:'+os.sep,'Users','Administrator','Desktop','水池_结果.xlsx')
N=10
lg=lambda m:print(time.strftime('%H:%M:%S'),m,flush=True)

def cdp():
    p=json.loads(urllib.request.urlopen('http://[::1]:%d/json'%CP,timeout=5).read())
    c=websocket.create_connection('ws://[::1]:%d/devtools/page/'%CP+p[0]['id'],timeout=5)
    return c

n=[0];c=cdp()
def js(cd):
    n[0]+=1
    c.send(json.dumps({'id':n[0],'method':'Runtime.evaluate','params':{'expression':cd,'returnByValue':True}}))
    c.settimeout(3)
    try:
        while True:
            r=json.loads(c.recv())
            if r.get('id')==n[0]:
                rs=r.get('result',{})
                return rs.get('result',{}).get('value','') if not rs.get('isException') else ''
    except:return ''

bid='navframe_135'
lg('Billing: '+bid)
eqid=''
ejs=js('(function(){var fs=document.querySelectorAll("iframe");for(var i=0;i<fs.length;i++){try{var d=fs[i].contentDocument;if(d&&d.getElementById("LOGIN_USER_ID"))return fs[i].id}catch(e){}}return""})()')
if ejs:eqid=ejs;lg('Equity: '+eqid)
else:
    eqid='eq_'+str(time.time()).replace('.','')
    js('(function(){var f=document.createElement("iframe");f.id="'+eqid+'";f.style.display="none";f.src="/ordercentre/ordercentre?service=page/oc.person.cs.fusion.Equitypoolquery&listener=onInitBusi&MENU_ID=FUSE20210917";document.body.appendChild(f);return"ok";})()')
    time.sleep(5)

wb=openpyxl.load_workbook(SR);ws=wb.active
all_phones=[str(ws.cell(r,1).value or'').strip() for r in range(2,ws.max_row+1) if ws.cell(r,1).value]
lg(str(len(all_phones))+' total')
ST=0
if os.path.exists(OU):
    try:
        wb2=openpyxl.load_workbook(OU);done=wb2.active.max_row-1
        if done>0:ST=done
    except:
        try:os.remove(OU);ST=0
        except:pass
if ST>=len(all_phones):lg('ALL DONE!');c.close();exit()
if ST==0:
    wb2=openpyxl.Workbook();osx=wb2.active
    osx.append(['号码','姓','套餐','全球通','年ARPU','余额','状态','权益金余额'])
else:
    wb2=openpyxl.load_workbook(OU);osx=wb2.active
phs=all_phones[ST:ST+N]
lg('Batch '+str(ST+1)+'-'+str(ST+len(phs)))
for ph in phs:
    ph=ph.strip();cust='';offer='';gt='';ya='';bal='';st='';eqb=''
    try:
        js('document.getElementById("'+bid+'").contentDocument.getElementById("ACCESS_NUMBER").value="'+ph+'"')
        tmp=js('(function(){try{var w=document.getElementById("'+bid+'").contentWindow;window.__CDP_RES__=null;w.agentUtil.ajax({url:"AgentCentre.person.payment.IAgentPaymentSV.queryBaseInfoPayment",refreshCust:true,data:{ACCESS_NUMBER:"'+ph+'",REMOVE_TAG:""},success:function(rr){window.__CDP_RES__=rr;}});return"ok";}catch(e){return"err:"+e.message;}})()')
        if tmp=='ok':
            time.sleep(3)
            r=js('window.__CDP_RES__?JSON.stringify(window.__CDP_RES__):"null"')
            if r and r!='null':
                dd=json.loads(r).get('DATA',{})
                c2=dd.get('CUST_NAME','') or ''
                cust=c2[:1] if c2 else ''
                offer=dd.get('OFFER_NAME','') or ''
                gt=dd.get('GOTONE_YEAR_LEVEL_NAME','') or ''
                ya=dd.get('GOTONE_YEAR_ARPU','') or ''
                bal=dd.get('GEN_BALANCE','') or ''
                st=dd.get('X_SVCSTATE_EXPLAIN','') or ''
            else:st='无数据'
        else:st='API失败'
    except:st='异常'
    try:
        js('document.getElementById("'+eqid+'").contentDocument.getElementById("ACCESS_NUMBER").value="'+ph+'"')
        js('document.getElementById("'+eqid+'").contentDocument.getElementById("LOGIN_USER_ID").value="'+ph+'"')
        js('document.getElementById("'+eqid+'").contentDocument.getElementById("LOGIN_USER_ID").dispatchEvent(new Event("input",{bubbles:true}))')
        time.sleep(1)
        js('document.getElementById("'+eqid+'").contentWindow.checkBaseQuery()')
        time.sleep(3)
        t=js('document.getElementById("'+eqid+'").contentDocument.body.innerText')
        for ln in(t or '').split('\n'):
            s=ln.strip()
            if u'\u6743\u76ca\u91d1\u4f59\u989d' in s:
                p=s.split('\uff1a')
                if len(p)>1:eqb=p[-1].strip()
    except:eqb='err'
    osx.append([ph,cust,offer,gt,ya,bal,st,eqb])
    try:wb2.save(OU)
    except:pass
try:wb2.save(OU)
except:pass
c.close()
lg('DONE! '+str(len(phs))+' phones')
