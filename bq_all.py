# -*- coding: utf-8 -*-
# 综合查号：billing + 权益金，用现有CRM页面iframe
import websocket,json,urllib.request,time,openpyxl,os,sys
CP=19222
SR=os.path.join('C:'+os.sep,'Users','Administrator','Desktop','水池.xlsx')
OU=os.path.join('C:'+os.sep,'Users','Administrator','Desktop','水池_结果.xlsx')
ST=0  # 起始行偏移
N=5   # 每次查N个号

lg=lambda m:print(time.strftime('%H:%M:%S'),m,flush=True)

# Connect CDP
try:
    p=json.loads(urllib.request.urlopen('http://[::1]:%d/json'%CP,timeout=3).read())
    c=websocket.create_connection('ws://[::1]:%d/devtools/page/'%CP+p[0]['id'],timeout=5)
except Exception as e:lg('CDP FAIL:'+str(e));exit()

n=0
def js(cd):
    global n;n+=1
    c.send(json.dumps({'id':n,'method':'Runtime.evaluate','params':{'expression':cd,'returnByValue':True}}))
    c.settimeout(10)
    try:
        while True:
            r=json.loads(c.recv())
            if r.get('id')==n:
                rs=r.get('result',{})
                if rs.get('isException'):return''
                return rs.get('result',{}).get('value','')
    except:return ''

# Phase 1: Find billing iframe (navframe with agentUtil + ACCESS_NUMBER)
lg('Finding billing iframe...')
fjs=js('Array.from(document.querySelectorAll("iframe")).filter(function(f){try{var d=f.contentDocument;return d&&d.getElementById("ACCESS_NUMBER")&&d.defaultView&&d.defaultView.agentUtil&&f.src.indexOf("payment")>-1}catch(e){return false}}).map(function(f){return f.id})')
lg('Billing iframes: '+fjs)
bid=''
if fjs and fjs!='[]':
    bid=json.loads(fjs)[0]
if not bid:
    lg('No billing iframe found! Need to click 代收话费 first.')
    exit()
lg('Using billing iframe: '+bid)

# Phase 2: Find or create equity iframe
lg('Finding equity iframe...')
eqjs=js('Array.from(document.querySelectorAll("iframe")).filter(function(f){try{var d=f.contentDocument;return d&&d.getElementById("LOGIN_USER_ID")&&f.src.indexOf("Equity")>-1}catch(e){return false}}).map(function(f){return f.id+":"+f.src.substring(0,40)})')
lg('Equity iframes: '+str(eqjs[:200]))
eqid=''
eqs=json.loads(eqjs) if eqjs and eqjs.startswith('[') else []
if eqs:eqid=eqs[0].split(':')[0]
if not eqid:
    lg('Creating equity iframe...')
    uid=str(time.time()).replace('.','')
    eqid='eq_'+uid
    js('(function(){var f=document.createElement("iframe");f.id="'+eqid+'";f.style.display="none";f.src="/ordercentre/ordercentre?service=page/oc.person.cs.fusion.Equitypoolquery&listener=onInitBusi&MENU_ID=FUSE20210917";document.body.appendChild(f);return"ok";})()')
    time.sleep(5)
lg('Using equity iframe: '+eqid)

# Phase 3: Load phones
wb=openpyxl.load_workbook(SR)
ws=wb.active
all_phones=[str(ws.cell(r,1).value or'').strip() for r in range(2,ws.max_row+1) if ws.cell(r,1).value]
lg(str(len(all_phones))+' phones total')

# Skip already processed
if os.path.exists(OU):
    try:
        wb2=openpyxl.load_workbook(OU)
        done=wb2.active.max_row-1
        if done>0:ST=done
    except:pass
phs=all_phones[ST:ST+N]
if not phs:lg('All done!');c.close();exit()

lg('Batch '+str(ST+1)+'-'+str(ST+len(phs)))

# Init result workbook
if ST==0:
    wb2=openpyxl.Workbook()
    osx=wb2.active
    osx.append(['号码','姓','套餐','全球通','年ARPU','月ARPU','余额','状态','权益金余额','权益金上限'])
else:
    wb2=openpyxl.load_workbook(OU)
    osx=wb2.active

# Process each phone
for idx,ph in enumerate(phs):
    lg(str(idx+1)+'/'+str(len(phs))+': '+ph)
    cust='';offer='';gt='';ya='';ma='';bal='';st='';eqb='';eql=''

    # Billing
    try:
        js('document.getElementById("'+bid+'").contentDocument.getElementById("ACCESS_NUMBER").value="'+ph+'"')
        tmp=js('(function(){try{var w=document.getElementById("'+bid+'").contentWindow;window.__CDP_RES__=null;w.agentUtil.ajax({url:"AgentCentre.person.payment.IAgentPaymentSV.queryBaseInfoPayment",refreshCust:true,data:{ACCESS_NUMBER:"'+ph+'",REMOVE_TAG:""},success:function(rr){window.__CDP_RES__=rr;}});return"ok";}catch(e){return"err:"+e.message;}})()')
        if tmp=='ok':
            time.sleep(3)
            r=js('window.__CDP_RES__?JSON.stringify(window.__CDP_RES__):"null"')
            if r and r!='null':
                dd=json.loads(r).get('DATA',{})
                c2=dd.get('CUST_NAME','') or ''
                cust=c2[0] if len(c2)>1 else c2
                offer=dd.get('OFFER_NAME','') or ''
                gt=dd.get('GOTONE_YEAR_LEVEL_NAME','') or ''
                ya=dd.get('GOTONE_YEAR_ARPU','') or ''
                ma=dd.get('GOTONE_MONTH_ARPU','') or ''
                bal=dd.get('GEN_BALANCE','') or ''
                st=dd.get('X_SVCSTATE_EXPLAIN','开') or '开'
            else:
                st='无数据'
        else:
            st='API失败'
    except Exception as e:
        st='异常:'+str(e)[:30]

    # Equity
    try:
        js('document.getElementById("'+eqid+'").contentDocument.getElementById("ACCESS_NUMBER").value="'+ph+'"')
        js('document.getElementById("'+eqid+'").contentDocument.getElementById("LOGIN_USER_ID").value="'+ph+'"')
        js('document.getElementById("'+eqid+'").contentDocument.getElementById("LOGIN_USER_ID").dispatchEvent(new Event("input",{bubbles:true}))')
        time.sleep(1)
        js('document.getElementById("'+eqid+'").contentWindow.checkBaseQuery()')
        time.sleep(3)
        t=js('document.getElementById("'+eqid+'").contentDocument.body.innerText')
        for line in (t or '').split('\n'):
            s=line.strip()
            if '\u6743\u76ca\u91d1\u4f59\u989d' in s:
                p=s.split('\uff1a')
                if len(p)>1:eqb=p[-1].strip()
            if '\u6743\u76ca\u91d1\u4e0a\u9650' in s:
                p=s.split('\uff1a')
                if len(p)>1:eql=p[-1].strip()
    except:
        eqb='err';eql=''

    osx.append([ph,cust,offer,gt,ya,ma,bal,st,eqb,eql])
    try:wb2.save(OU)
    except:pass

try:wb2.save(OU)
except:pass
lg('Done! '+str(len(phs))+' phones')
c.close()
