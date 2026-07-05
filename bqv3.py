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

def type_phone(ph):
    return js('(function(){try{var f=document.getElementById('+Q+'navframe_133'+Q+');if(!f)return"nf";var d=f.contentDocument||f.contentWindow.document;var e=d.getElementById('+Q+'ACCESS_NUMBER'+Q+');if(!e)return"noinput";e.value='+Q+ph+Q+';return"ok";}catch(e){return"err"}})()')

def get_cust_info():
    txt=js('(function(){try{return(document.body.innerText||"").substring(0,5000);}catch(e){return""}})()')
    lines=txt.split('\n')
    info={}
    for i,l in enumerate(lines):
        s=l.strip()
        if s=='客户姓名：' and i+1<len(lines):
            name=lines[i+1].strip()
            info['name']=name[0] if name else''
        elif s=='服务号码：' and i+1<len(lines):
            info['phone']=lines[i+1].strip()
        elif s=='主套餐：' and i+1<len(lines):
            info['plan']=lines[i+1].strip()
        elif s.find('全球通')>=0 and s.find('：')>=0:
            key=s.split('：')[0].strip()
            val=''
            if i+1<len(lines):val=lines[i+1].strip()
            if '月评' in key:info['card']=val
        elif s=='月评ARPU：' and i+1<len(lines):
            info['arpu_m']=lines[i+1].strip()
        elif s=='年评ARPU：' and i+1<len(lines):
            info['arpu_y']=lines[i+1].strip()
    return info

# Quick self-test
ph='15108742724'
info=get_cust_info()
lg('before:'+info.get('phone','')+info.get('name',''))

r=type_phone(ph)
lg('type:'+r)
time.sleep(1.5)
info=get_cust_info()
lg('after:'+info.get('phone','')+'/'+info.get('name','')+'/'+info.get('plan','')+'/'+info.get('card','')+'/'+info.get('arpu_m','')+'/'+info.get('arpu_y',''))
lg('exists:'+('yes' if info.get('name') else'no'))

if not info.get('name'):
    lg('FAIL:no customer info on main page')
    c.close()
    exit()

# Now batch process
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
        type_phone(ph)
        time.sleep(1.5)
        info=get_cust_info()
        if not info.get('name'):
            osx.append([ph,'','','','','','不存在'])
            fail+=1
        else:
            osx.append([ph,info.get('name',''),info.get('plan',''),info.get('card',''),info.get('arpu_y',''),info.get('arpu_m','')])
            ok+=1
    except Exception as e:
        osx.append([ph,'','','','','',str(e)[:100]])
        fail+=1
    time.sleep(0.3)

out.save(OU)
lg(str(ok)+'ok '+str(fail)+'fail')
c.close()
