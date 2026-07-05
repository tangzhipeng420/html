#!/usr/bin/env python3
"""BOSS批量查号"""
import websocket, json, time, openpyxl, re, os, sys
CDP_PORT = 19222
SRC = r"C:\Users\Administrator\Desktop\水池.xlsx"
OUT = r"C:\Users\Administrator\Desktop\水池_结果.xlsx"
def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)
def js(ws, mid, code, to=15):
    ws.send(json.dumps({"id":mid,"method":"Runtime.evaluate","params":{"expression":code,"returnByValue":True}}))
    d = time.time()+to
    while time.time()<d:
        try:
            r = json.loads(ws.recv())
            if r.get("id")==mid:
                res = r.get("result",{})
                if "exceptionDetails" in res: return ""
                return res.get("value","") or ""
        except: pass
    return ""
def find_page():
    for a in ["127.0.0.1","[::1]"]:
        try:
            import urllib.request
            pgs = json.loads(urllib.request.urlopen(f"http://{a}:{CDP_PORT}/json",timeout=5).read())
            for p in pgs:
                t = (p.get("title","") or "").lower()
                if any(x in t for x in ["crm","boss","客户关系"]): return p["id"], a
            if pgs: return pgs[0]["id"], a
        except: continue
    return None, None
def main():
    log("=== BOSS查号 ===")
    if not os.path.exists(SRC): log("找不到水池.xlsx"); return
    wb = openpyxl.load_workbook(SRC)
    ws = wb.active
    phones = [str(ws.cell(r,1).value or "").strip() for r in range(2, ws.max_row+1) if ws.cell(r,1).value is not None and str(ws.cell(r,1).value).strip()]
    if not phones: log("无号码"); return
    log(f"共{len(phones)}个")
    pid, addr = find_page()
    if not pid: log("SafeBrowser未启动"); return
    c = websocket.create_connection(f"ws://{addr}:{CDP_PORT}/devtools/page/{pid}", timeout=10)
    m = 1
    log("注入iframe...")
    js(c, m, """(function(){var fs=document.querySelectorAll('iframe');for(var i=0;i<fs.length;i++){var s=fs[i].src||'';if(s.indexOf('payment')>=0||s.indexOf('vc.P')>=0||s.indexOf('PCredit')>=0){fs[i].style.display='';return fs[i].id;}}var f=document.createElement('iframe');f.id='pf';f.src='https://agent.netvan.cn/agentcentre/agentcentre?service=page/person.payment.vc.PCreditPaymentQuery';f.style.width='100%';f.style.height='900px';document.body.appendChild(f);return 'created';})()""")
    m+=1; time.sleep(5)
    aids = js(c, m, "JSON.stringify(Array.from(document.querySelectorAll('iframe'),f=>f.id))")
    m+=1
    fid = ""
    for fn in json.loads(aids or "[]"):
        if js(c, m, f"(function(){{var f=document.getElementById('{fn}');try{{var d=f.contentDocument||f.contentWindow.document;return d.getElementById('ACCESS_NUMBER')?'ok':'';}}catch(e){{return'';}}}})()"):
            fid = fn; break
        m+=1
    if not fid: log("找不到查询框"); c.close(); return
    log(f"查询框: {fid}")
    out_wb = openpyxl.Workbook()
    out_ws = out_wb.active
    out_ws.append(["号码","结果","状态"])
    ok = fail = 0
    for idx, phone in enumerate(phones[:150]):
        log(f"[{ok+fail+1}] {phone}")
        try:
            js(c, m, f"(function(){{var f=document.getElementById('{fid}');try{{var d=f.contentDocument||f.contentWindow.document;d.getElementById('ACCESS_NUMBER').value='{phone}';return'ok';}}catch(e){{return'e:'+e.message;}}}})()")
            m+=1; time.sleep(1)
            js(c, m, f"(function(){{var f=document.getElementById('{fid}');try{{var d=f.contentDocument||f.contentWindow.document;var bs=d.querySelectorAll('button');for(var i=0;i<bs.length;i++){{if((bs[i].innerText||'').trim()=='\u67e5\u8be2'){{bs[i].click();return'ok';}}}}return'nf';}}catch(e){{return'e:'+e.message;}}}})()")
            m+=1; time.sleep(3)
            txt = ""
            for fn in json.loads(js(c, m, "JSON.stringify(Array.from(document.querySelectorAll('iframe'),f=>f.id))") or "[]"):
                t = js(c, m, f"(function(){{var f=document.getElementById('{fn}');if(!f)return'';try{{var d=f.contentDocument||f.contentWindow.document;return(d.body.innerText||'').substring(0,2000);}}catch(e){{return'';}}}})()")
                m+=1
                if len(t) > len(txt): txt = t
            info = [l.strip()[:80] for l in txt.split("\n") if l.strip() and any(k in l for k in ["客户","套餐","ARPU","全球通","余额","信用","姓名","状态","号码"])]
            out_ws.append([phone, " | ".join(info[:10]) or "(无数据)", "ok"])
            ok += 1
        except Exception as e:
            out_ws.append([phone, str(e)[:200], "err"])
            fail += 1
    out_wb.save(OUT)
    log(f"完成: {ok}成功 {fail}失败")
    c.close()
if __name__ == "__main__":
    main()
