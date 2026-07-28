#!/usr/bin/env python3
"""
Final version: update 各门店报量看板.html with July 27 data.
Handles column insertion correctly by tracking exact positions.
"""
import re

with open('/home/ubuntu/gh-pages/各门店报量看板.html.bak', 'r', encoding='utf-8') as f:
    html = f.read()

# =============================================
# Helper
# =============================================
def get_table_entries(html, table_idx):
    """Get table data: cols list, and list of (date_str, values_dict)."""
    tables = list(re.finditer(r'<table class="day-table">.*?</table>', html, re.DOTALL))
    t = tables[table_idx]
    table_html = t.group(0)
    
    hm = re.search(r'<tr><th>日期</th>(.*?)</tr>', table_html)
    raw = hm.group(1)
    # Parse: <th>NAME</th><th>NAME2</th>...
    cols = []
    for m in re.finditer(r'<th>([^<]+)</th>', raw):
        cols.append(m.group(1))
    
    entries = []
    for row_m in re.finditer(r'<tr><td>(\d+)日</td>(.*?)</tr>', table_html, re.DOTALL):
        date = row_m.group(1)
        vals = [v.strip() for v in row_m.group(2).split('</td><td>')]
        vals = [v.replace('<td>','').replace('</td>','').strip() for v in vals]
        entry = {}
        for i, v in enumerate(vals):
            if i < len(cols):
                entry[cols[i]] = v if v != '-' else '-'
        entries.append((date, entry))
    
    return cols, entries

def rebuild_table_html(cols, entries):
    """Build a day-table HTML from column list and entries."""
    header = '<tr><th>日期</th><th>' + '</th><th>'.join(cols) + '</th></tr>'
    rows = []
    for date, data in entries:
        vals = []
        for col in cols:
            v = data.get(col, '-')
            vals.append(str(v))
        rows.append(f'<tr><td>{date}日</td><td>' + '</td><td>'.join(vals) + '</td></tr>')
    return '<table class="day-table">\n' + header + '\n' + '\n'.join(rows) + '\n</table>'

def get_sums(cols, entries):
    """Return {col: sum}."""
    sums = {c: 0 for c in cols}
    for date, data in entries:
        for col in cols:
            v = data.get(col, '-')
            if v != '-' and str(v).isdigit():
                sums[col] += int(v)
    return sums

def replace_table(html, table_idx, new_table_html):
    """Replace table at given index with new HTML."""
    tables = list(re.finditer(r'<table class="day-table">.*?</table>', html, re.DOTALL))
    old = tables[table_idx].group(0)
    return html.replace(old, new_table_html)

def update_summary_tags_for_card(html, card_marker, tag_map):
    """Replace summary-row for a store card. card_marker is unique identifier."""
    idx = html.find(card_marker)
    if idx == -1:
        print(f"  ERROR: Card marker '{card_marker}' not found")
        return html
    chunk = html[idx:idx+5000]
    sm = re.search(r'(<div class="summary-row">)(.*?)(</div>\s*<div class="sc-wrap">)', chunk, re.DOTALL)
    if sm:
        old = sm.group(0)
        tag_htmls = []
        for label, val in tag_map.items():
            if val == 0:
                continue
            cls = 'summary-tag'
            if '手机' in label: cls += ' s-phone'
            if '开户' in label: cls += ' s-open'
            if '宽带' in label: cls += ' s-broad'
            tag_htmls.append(f'<span class="{cls}">{label} {val}</span>')
        new = sm.group(1) + '\n' + '\n'.join(tag_htmls) + '\n' + sm.group(3)
        return html.replace(old, new)
    else:
        # Handle the 新平 case which is inside <div class="grand">
        chunk2 = html[idx:idx+5000]
        sm2 = re.search(r'(<div class="summary-row">)(.*?)(</div>\s*<table class="day-table">)', chunk2, re.DOTALL)
        if sm2:
            old = sm2.group(0)
            tag_htmls = []
            for label, val in tag_map.items():
                if val == 0:
                    continue
                cls = 'summary-tag'
                if '手机' in label: cls += ' s-phone'
                if '开户' in label: cls += ' s-open'
                if '宽带' in label: cls += ' s-broad'
                tag_htmls.append(f'<span class="{cls}">{label} {val}</span>')
            new = sm2.group(1) + '\n' + '\n'.join(tag_htmls) + '\n' + sm2.group(3)
            return html.replace(old, new)
        print(f"  ERROR: Could not find summary-row for '{card_marker}'")
        return html

def update_summary_tags_for_xinping(html, tag_map):
    """Special handling for xinping which uses a different structure."""
    idx = html.find('📞 新平外呼组')
    if idx == -1:
        print("  ERROR: 新平 not found")
        return html
    chunk = html[idx:idx+5000]
    sm = re.search(r'(<div class="summary-row">)(.*?)(</div>)', chunk, re.DOTALL)
    if sm and '</div>\n<table' not in sm.group(2) and '</div>\n<div' not in sm.group(2):
        # This is the right summary-row
        pass
    else:
        sm = re.search(r'(<div class="summary-row">)(.*?)(</div>\s*<table class="day-table">)', chunk, re.DOTALL)
    
    if not sm:
        print("  ERROR: Could not find 新平 summary-row")
        return html
    
    old = sm.group(0)
    tag_htmls = []
    for label, val in tag_map.items():
        if val == 0:
            continue
        cls = 'summary-tag'
        if '手机' in label: cls += ' s-phone'
        if '开户' in label: cls += ' s-open'
        if '宽带' in label: cls += ' s-broad'
        tag_htmls.append(f'<span class="{cls}">{label} {val}</span>')
    new = sm.group(1) + '\n' + '\n'.join(tag_htmls) + '\n' + sm.group(3)
    return html.replace(old, new)


# =============================================
# TABLE 0: 峨山店
# =============================================
print("=== 峨山店 ===")
cols0, entries0 = get_table_entries(html, 0)
print(f"Original cols: {cols0}")

# Add 高清盒 after 高清盒续费
if '高清盒' not in cols0:
    idx_hd = cols0.index('高清盒续费')
    cols0.insert(idx_hd + 1, '高清盒')
if '碎屏险' not in cols0:
    cols0.append('碎屏险')

# Add 27日 data (keeping all values from original data + new 27日)
# Original data stays the same, we just add a new entry
entries0.append(('27', {
    '开户': 2, '高清盒': 1, '58畅享包': 1, '宽带': 10, '路由器': 9, '安全管家仿诈': 3, '碎屏险': 0
}))

new_table0 = rebuild_table_html(cols0, entries0)
html = replace_table(html, 0, new_table0)

# Recompute sums
sums0 = get_sums(cols0, entries0)
print(f"峨山 sums: {{k:v for k,v in sums0.items() if v>0}}")

eshan_tags = {
    '📱手机': sums0.get('手机', 0),
    '📋开户': sums0.get('开户', 0),
    '29小福袋': sums0.get('29小福袋', 0),
    '29流量包': sums0.get('29流量包', 0),
    '畅享包': sums0.get('畅享包', 0),
    '畅享包升级版': sums0.get('畅享包升级版', 0),
    '机顶盒': sums0.get('机顶盒', 0),
    '机顶盒包年': sums0.get('机顶盒包年', 0),
    '高清盒包年': sums0.get('高清盒包年', 0),
    '高清盒续费': sums0.get('高清盒续费', 0),
    '高清盒': sums0.get('高清盒', 0),
    '158畅享包': sums0.get('158畅享包', 0),
    '118畅享包': sums0.get('118畅享包', 0),
    '电子学生证': sums0.get('电子学生证', 0),
    '全球通宽带': sums0.get('全球通宽带', 0),
    '路由器': sums0.get('路由器', 0),
    '电饭煲': sums0.get('电饭煲', 0),
    '39小福袋': sums0.get('39小福袋', 0),
    '39流量包': sums0.get('39流量包', 0),
    'V网': sums0.get('V网', 0),
    '安全管家仿诈': sums0.get('安全管家仿诈', 0),
    '视频彩铃plus': sums0.get('视频彩铃plus', 0),
    '和校园': 3,
    '顺差碎屏险': 12,
    '摄像头': 1,
    '流量翻番包': 2,
    '碎屏险': sums0.get('碎屏险', 0),
}
html = update_summary_tags_for_card(html, '<!-- 峨山店 -->', eshan_tags)

# =============================================
# TABLE 1: 加盟厅
# =============================================
print("=== 加盟厅 ===")
cols1, entries1 = get_table_entries(html, 1)  # Re-fetch after html change
print(f"Original cols: {cols1}")

if '88会员' not in cols1:
    cols1.append('88会员')
if '29小福袋' not in cols1:
    cols1.append('29小福袋')

entries1.append(('27', {
    '开户': 4, '手机': 2, '轻合约+碎屏险': 1, '29小福袋': 1, '畅享包': 1, '88会员': 5, '短信免打扰': 5, '高频防骚扰': 5
}))

new_table1 = rebuild_table_html(cols1, entries1)
html = replace_table(html, 1, new_table1)

sums1 = get_sums(cols1, entries1)
print(f"加盟 sums: { {k:v for k,v in sums1.items() if v>0} }")

jm_tags = {
    '📱手机': sums1.get('手机', 0),
    '📋开户': sums1.get('开户', 0),
    '轻合约+碎屏险': sums1.get('轻合约+碎屏险', 0),
    '集团V网': sums1.get('集团V网', 0),
    '电视续费包年': sums1.get('电视续费包年', 0),
    '畅享包': sums1.get('畅享包', 0),
    '平板': sums1.get('平板', 0),
    '短信免打扰': sums1.get('短信免打扰', 0),
    '高频防骚扰': sums1.get('高频防骚扰', 0),
    '88会员': sums1.get('88会员', 0),
    '29小福袋': sums1.get('29小福袋', 0),
    '电饭煲': sums1.get('电饭煲', 0),
}
html = update_summary_tags_for_card(html, '<!-- 加盟厅 -->', jm_tags)

# =============================================
# TABLE 2: 京东店
# =============================================
print("=== 京东店 ===")
cols2, entries2 = get_table_entries(html, 2)
print(f"Original cols: {cols2}")

if '笔记本电脑' not in cols2:
    cols2.append('笔记本电脑')
if '88会员年包' not in cols2:
    cols2.append('88会员年包')
if '88会员' not in cols2:
    cols2.append('88会员')

entries2.append(('27', {
    '手机': 1, '笔记本电脑': 1, '学生证': 1, '开户': 1, '39元开户': 2, '88会员年包': 9, '88会员': 9, '短信免打扰': 3, '高频防骚扰': 4
}))

new_table2 = rebuild_table_html(cols2, entries2)
html = replace_table(html, 2, new_table2)

sums2 = get_sums(cols2, entries2)
print(f"京东 sums: { {k:v for k,v in sums2.items() if v>0} }")

mobile_total2 = sums2.get('手机', 0) + sums2.get('轻合约+手机', 0)
open_total2 = sums2.get('开户', 0) + sums2.get('9元开户', 0) + sums2.get('39元开户', 0) + sums2.get('59元开户', 0)

jd_tags = {
    '📱手机（含轻合约）': mobile_total2,
    '📋开户（含9/39/59元）': open_total2,
    '轻合约+手机': sums2.get('轻合约+手机', 0),
    '单独手机': sums2.get('手机', 0),
    '畅享包': sums2.get('畅享包', 0),
    '集团V网': sums2.get('集团V网', 0),
    '智能手表': sums2.get('智能手表', 0),
    '学生证': sums2.get('学生证', 0),
    '短信免打扰': sums2.get('短信免打扰', 0),
    '高频防骚扰': sums2.get('高频防骚扰', 0),
    '平板': sums2.get('平板', 0),
    '小天才手表': sums2.get('小天才手表', 0),
    '空气炸锅': sums2.get('空气炸锅', 0),
    '笔记本电脑': sums2.get('笔记本电脑', 0),
    '88会员年包': sums2.get('88会员年包', 0),
    '88会员': sums2.get('88会员', 0),
}
html = update_summary_tags_for_card(html, '<!-- 京东店 -->', jd_tags)

# =============================================
# TABLE 3: 新平外呼组
# =============================================
print("=== 新平外呼组 ===")
cols3, entries3 = get_table_entries(html, 3)
print(f"Original cols: {cols3}")

if '碎屏险' not in cols3:
    cols3.append('碎屏险')
if '88会员年包' not in cols3:
    cols3.append('88会员年包')
if '集团V网' not in cols3:
    cols3.append('集团V网')

entries3.append(('27', {
    '新开户': 3, '手机': 1, '碎屏险': 2, '电子学生证': 1, '视频彩铃PLUS': 8,
    '电饭煲/空气炸锅': 3, '升档大促': 2, '宽带升千': 10, '88会员年包': 35,
    '电视续费': 1, '全球通宽带': 4, 'WiFi': 4, '集团V网': 3
}))

new_table3 = rebuild_table_html(cols3, entries3)
html = replace_table(html, 3, new_table3)

sums3 = get_sums(cols3, entries3)
print(f"新平 sums: { {k:v for k,v in sums3.items() if v>0} }")

xp_tags = {
    '新开户': sums3.get('新开户', 0),
    '畅享包': sums3.get('畅享包', 0),
    '📱手机': sums3.get('手机', 0),
    '电子学生证': sums3.get('电子学生证', 0),
    '儿童手表': sums3.get('儿童手表', 0),
    '29手机福袋': sums3.get('29手机福袋', 0),
    '9.9亲情守护': sums3.get('9.9亲情守护', 0),
    '视频彩铃PLUS': sums3.get('视频彩铃PLUS', 0),
    '电视续费': sums3.get('电视续费', 0),
    '升档大促': sums3.get('升档大促', 0),
    '宽带升千': sums3.get('宽带升千', 0),
    '全球通宽带': sums3.get('全球通宽带', 0),
    'WiFi': sums3.get('WiFi', 0),
    '电饭煲/空气炸锅': sums3.get('电饭煲/空气炸锅', 0),
    '碎屏险': sums3.get('碎屏险', 0),
    '88会员年包': sums3.get('88会员年包', 0),
    '集团V网': sums3.get('集团V网', 0),
}
html = update_summary_tags_for_xinping(html, xp_tags)

# =============================================
# Grand total table
# =============================================
print("=== Grand Total ===")

# Re-parse all summary tags
def parse_card_summary(html, marker):
    idx = html.find(marker)
    if idx == -1: return {}
    chunk = html[idx:idx+5000]
    sm = re.search(r'<div class="summary-row">(.*?)</div>', chunk, re.DOTALL)
    if not sm: return {}
    pairs = re.findall(r'<span class="summary-tag[^"]*">([^<]+?)</span>', sm.group(1))
    tags = {}
    for p in pairs:
        parts = p.strip().rsplit(' ', 1)
        if len(parts) == 2 and parts[1].isdigit():
            tags[parts[0]] = int(parts[1])
    return tags

eshan_tag = parse_card_summary(html, '<!-- 峨山店 -->')
jm_tag = parse_card_summary(html, '<!-- 加盟厅 -->')
jd_tag = parse_card_summary(html, '<!-- 京东店 -->')
xp_tag = parse_card_summary(html, '📞 新平外呼组')

print(f"Eshan: {eshan_tag}")
print(f"Jiameng: {jm_tag}")
print(f"Jingdong: {jd_tag}")
print(f"Xinping: {xp_tag}")

def fmt_val(v):
    return str(v) if v else '-'

def update_grand(html, key_text, e, jm, jd, xp):
    total = e + jm + jd + xp
    escaped = re.escape(key_text)
    pattern = rf'<tr><td>[^<]*?{escaped}[^<]*?</td><td[^>]*?>([^<]+)</td><td[^>]*?>([^<]+)</td><td[^>]*?>([^<]+)</td><td[^>]*?>([^<]+)</td><td[^>]*?>([^<]+)</td></tr>'
    m = re.search(pattern, html)
    if m:
        old = m.group(0)
        prefix = re.search(rf'(<tr><td>[^<]*?{escaped}[^<]*?</td>)', old).group(1)
        new = f'{prefix}<td style="color:#1565c0">{fmt_val(e)}</td><td style="color:#7b1fa2">{fmt_val(jm)}</td><td style="color:#2e7d32">{fmt_val(jd)}</td><td style="color:#e65100">{fmt_val(xp)}</td><td style="background:#e3f2fd;font-weight:700">{total}</td></tr>'
        html = html.replace(old, new)
        print(f"  Grand row '{key_text}' updated: {e}/{jm}/{jd}/{xp} = {total}")
    else:
        print(f"  WARNING: Grand row '{key_text}' not found!")
    return html

html = update_grand(html, '手机（含合约）', eshan_tag.get('📱手机',0), jm_tag.get('📱手机',0), jd_tag.get('📱手机（含轻合约）',0), xp_tag.get('📱手机',0))
html = update_grand(html, '开户', eshan_tag.get('📋开户',0), jm_tag.get('📋开户',0), jd_tag.get('📋开户（含9/39/59元）',0), xp_tag.get('新开户',0))
html = update_grand(html, '学生证', eshan_tag.get('电子学生证',0), 0, jd_tag.get('学生证',0), 0)
html = update_grand(html, '小福袋', eshan_tag.get('29小福袋',0), jm_tag.get('29小福袋',0), 0, xp_tag.get('29手机福袋',0))
html = update_grand(html, '轻合约', 0, jm_tag.get('轻合约+碎屏险',0), jd_tag.get('轻合约+手机',0), 0)
html = update_grand(html, '视频彩铃', eshan_tag.get('视频彩铃plus',0), 0, 0, xp_tag.get('视频彩铃PLUS',0))
html = update_grand(html, '免打扰/防骚扰', 0, jm_tag.get('短信免打扰',0)+jm_tag.get('高频防骚扰',0), jd_tag.get('短信免打扰',0)+jd_tag.get('高频防骚扰',0), 0)
eshan_tv = eshan_tag.get('机顶盒',0)+eshan_tag.get('机顶盒包年',0)+eshan_tag.get('高清盒包年',0)+eshan_tag.get('高清盒续费',0)+eshan_tag.get('高清盒',0)
html = update_grand(html, '电视/机顶盒', eshan_tv, jm_tag.get('电视续费包年',0), 0, xp_tag.get('电视续费',0))
html = update_grand(html, '宽带升千', 0, 0, 0, xp_tag.get('宽带升千',0))
html = update_grand(html, '全球通宽带', eshan_tag.get('全球通宽带',0), 0, 0, xp_tag.get('全球通宽带',0))
html = update_grand(html, 'WiFi', 0, 0, 0, xp_tag.get('WiFi',0))

# =============================================
# Write output
# =============================================
with open('/home/ubuntu/gh-pages/各门店报量看板.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("\n=== DONE ===")
