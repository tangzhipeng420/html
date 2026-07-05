import websocket,json,urllib.request,time,openpyxl,os,sys
CP=19222
SR=os.path.join('C:','Users','Administrator','Desktop','pool.xlsx')
OU=os.path.join('C:','Users','Administrator','Desktop','pool_r.xlsx')

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

Q='"'  # JS double quote

v=js('(function(){try{var f=document.getElementById('+Q++navframe_133'+Q+');if(!f)return"nf";var d=f.contentDocument||f.contentWindow.document;var e=d.getElementById('+Q+'ACCESS_NUMBER'+Q+');return e?"ok:"+e.value:"no"}catch(e){return"err"}})()')
lg('133:'+v[:40])
fn='navframe_133'
if not v.startswith('ok'):
    v=js('(function(){try{var f=document.getElementById('+Q++navframe_161'+Q+');var d=f.contentDocument||f.contentWindow.document;var e=d.getElementById('+Q+'ACCESS_NUMBER'+Q+');return e?"ok:"+e.value:"no"}catch(e){return"err"}})()')
    lg('161:'+v[:40])
    if v.startswith('ok'):fn='navframe_161'
if not v.startswith('ok'):lg('FAIL');c.close();exit()
lg('USE:'+fn)

if not os.path.exists(SR):lg('no pool');c.close();exit()
wb=openpyxl.load_workbook(SR);ws=wb.active
phs=[str(ws.cell(r,1).value or'').strip() for r in range(2,ws.max_row+1)if ws.cell(r,1).value and str(ws.cell(r,1).value).strip()]
lg('total:'+str(len(phs)))

out=openpyxl.Workbook();osx=out.active
osx.append(['phone','result','status'])
ok=fail=0

for idx,ph in enumerate(phs[:3]):
    lg(f'[{ok+fail+1}] {ph}')
    try:
        r=js('(function(){try{var f=document.getElementById('+Q+fn+Q+');var d=f.contentDocument||f.contentWindow.document;d.getElementById('+Q+'ACCESS_NUMBER'+Q+').value='+Q+ph+Q+';return"ok";}catch(e){return"err"}})()')
        if not r.startswith('ok'):raise Exception(str(r)[:50])
        time.sleep(0.5)
        r=js('(function(){try{var f=document.getElementById('+Q+fn+Q+');var d=f.contentDocument||f.contentWindow.document;var bs=d.querySelectorAll("button");for(var i=0;i<bs.length;i++){if(bs[i].innerText.trim()=="\u67e5\u8be2"){bs[i].click();return"ok";}}return"nf";}catch(e){return"err"}})()')
        if not r.startswith('ok'):raise Exception('nobtn:'+str(r)[:30])
        time.sleep(3)
        txt=js('(function(){try{var f=document.getElementById('+Q+fn+Q+');var d=f.contentDocument||f.contentWindow.document;return(d.body.innerText||"").substring(0,3000);}catch(e){return""}})()')
        info=[l.strip()[:80]for l in txt.split(chr(10))if l.strip()and any(k in l for k in['name','plan','ARPU','balance','fee','status','号码','套餐','余额','客户'])]
        osx.append([ph,' | '.join(info[:8])or'(-)','ok'])
        ok+=1
    except Exception as e:
        osx.append([ph,str(e)[:200],'err'])
        fail+=1
    time.sleep(0.5)

out.save(OU)
lg(str(ok)+'ok '+str(fail)+'fail')
c.close()