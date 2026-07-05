# -*- coding: utf-8 -*-
# 综合查号：billing + 权益金，→键暂停，每日上限130
import websocket,json,urllib.request,time,openpyxl,os,msvcrt
CP=19222;SR=os.path.join('C:'+os.sep,'Users','Administrator','Desktop','水池.xlsx')
OU=os.path.join('C:'+os.sep,'Users','Administrator','Desktop','水池_结果.xlsx')
DAILY_LIMIT=130
lg=lambda m:print(time.strftime('%H:%M:%S'),m,flush=True)

def check_pause():
    if msvcrt.kbhit():
        k=msvcrt.getch()
        if k==b'\xe0':
            k2=msvcrt.getch()
            if k2==b'M':
                lg('→ PAUSE')
                return True
    return False

def cdp_conn():
    p=json.loads(urllib.request.urlopen('http://[::1]:%d/json'%CP,timeout=5).read())
    return websocket.create_connection('ws://[::1]:%d/devtools/page/'%CP+p[0]['id'],timeout=5)

def setup(c):
    n=[0]
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
    js('try{var es=document.querySelectorAll(".dialog-close,.closeBtn,.layui-layer-close");for(var i=0;i<es.length;i++)es[i].click()}catch(e){}')
    js('try{var bs=document.querySelectorAll(".layui-layer-btn0,.layui-layer-btn1");for(var i=0;i<bs.length;i++)bs[i].click()}catch(e){}')
    bid='navframe_135'
    eqid=''
    ejs=js('(function(){var fs=document.querySelectorAll("iframe");for(var i=0;i<fs.length;i++){try{var d=fs[i].contentDocument;if(d&&d.getElementById("LOGIN_USER_ID"))return fs[i].id}catch(e){}}return""})()')
    if ejs:eqid=ejs
    else:
        eqid='eq_'+str(time.time()).replace('.','')
        js('(function(){var f=document.createElement("iframe");f.id="'+eqid+'";f.style.display="none";f.src="/ordercentre/ordercentre?service=page/oc.person.cs.fusion.Equitypoolquery&listener=onInitBusi&MENU_ID=FUSE20210917";document.body.appendChild(f);return"ok";})()')
        time.sleep(5)
    return bid,eqid,js

def dismiss(js):
    js('try{var es=document.querySelectorAll(".dialog-close,.closeBtn,.layui-layer-close");for(var i=0;i<es.length;i++)es[i].click()}catch(e){}')
    js('try{var bs=document.querySelectorAll(".layui-layer-btn0,.layui-layer-btn1");for(var i=0;i<bs.length;i++)bs[i].click()}catch(e){}')

def query_one(ph,bid,eqid,js):
    cust='';offer='';gt='';ya='';bal='';st='';eqb=''
    dismiss(js)
    try:
        js('document.getElementById("'+bid+'").contentDocument.getElementById("ACCESS_NUMBER").value="'+ph+'"')
        tmp=js('(function(){try{var w=document.getElementById("'+bid+'").contentWindow;window.__CDP_RES__=null;w.agentUtil.ajax({url:"AgentCentre.person.payment.IAgentPaymentSV.queryBaseInfoPayment",refreshCust:true,data:{ACCESS_NUMBER:"'+ph+'",REMOVE_TAG:""},success:function(rr){window.__CDP_RES__=rr;}});return"ok";}catch(e){return"err:"+e.message;}})()')
        if tmp=='ok':
            time.sleep(2)
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
    dismiss(js)
    try:
        js('document.getElementById("'+eqid+'").contentDocument.getElementById("ACCESS_NUMBER").value="'+ph+'"')
        js('document.getElementById("'+eqid+'").contentDocument.getElementById("LOGIN_USER_ID").value="'+ph+'"')
        js('document.getElementById("'+eqid+'").contentDocument.getElementById("LOGIN_USER_ID").dispatchEvent(new Event("input",{bubbles:true}))')
        time.sleep(1)
        js('document.getElementById("'+eqid+'").contentWindow.checkBaseQuery()')
        time.sleep(2)
        t=js('document.getElementById("'+eqid+'").contentDocument.body.innerText')
        for ln in(t or '').split('\n'):
            s=ln.strip()
            if u'\u6743\u76ca\u91d1\u4f59\u989d' in s:
                p=s.split('\uff1a')
                if len(p)>1:eqb=p[-1].strip()
    except:eqb='err'
    return [ph,cust,offer,gt,ya,bal,st,eqb]

# Main
wb0=openpyxl.load_workbook(SR);ws0=wb0.active
all_phones=[str(ws0.cell(r,1).value or'').strip() for r in range(2,ws0.max_row+1) if ws0.cell(r,1).value]
total=len(all_phones);lg(str(total)+' total')
ST=0
if os.path.exists(OU):
    try:
        wb2=openpyxl.load_workbook(OU);done=wb2.active.max_row-1
        if done>0:ST=done
    except:
        try:os.remove(OU);ST=0
        except:pass
if ST>=total:lg('ALL DONE!');exit()
ph_count=min(DAILY_LIMIT,total-ST)
if ST==0:
    wb2=openpyxl.Workbook();osx=wb2.active
    osx.append(['号码','姓','套餐','全球通','年ARPU','余额','状态','权益金余额'])
else:
    wb2=openpyxl.load_workbook(OU);osx=wb2.active
phs=all_phones[ST:ST+ph_count]
lg('Run: '+str(ST+1)+'-'+str(ST+len(phs))+' ('+str(len(phs))+'/'+str(DAILY_LIMIT)+')')
lg('→ 按键盘 → 键暂停')
paused=False
try:
    c=cdp_conn();bid,eqid,js=setup(c)
    fail_bi=0
    for i,ph in enumerate(phs):
        if check_pause():
            paused=True;break
        ph=ph.strip()
        lg('%d/%d: %s'%(i+1+ST,total,ph))
        row=query_one(ph,bid,eqid,js)
        osx.append(row)
        if row[6] in ('API失败','异常'):
            fail_bi+=1
            if fail_bi>=3:
                lg('Reloading billing...')
                dismiss(js)
                js('try{document.getElementById("'+bid+'").src="/agentcentre/agentcentre?service=page/person.payment.vc.Payment&listener=onInitBusi&MENU_ID=1"}catch(e){}')
                time.sleep(3);fail_bi=0
        else:fail_bi=0
        try:wb2.save(OU)
        except:pass
        if (i+1)%5==0 and i+1<len(phs):
            lg('Reconnecting CDP...')
            c.close();c=cdp_conn();bid,eqid,js=setup(c)
    c.close()
except Exception as e:
    lg('Error: '+str(e)[:60])
    try:wb2.save(OU)
    except:pass
reach=ST+len(phs)-1 if paused else ST+len(phs)
if paused:
    lg('已暂停（→键），进度已保存。下次重跑自动继续')
else:
    lg('今日已完成 '+str(len(phs))+' 个')
if reach<total:lg('还剩 '+str(total-reach)+' 个，明天继续')
