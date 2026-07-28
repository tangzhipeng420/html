#!/usr/bin/env python3
"""
Final version: minimal, targeted updates to the HTML.
Only changes:
1. Notice bar date
2. Header date
3. Footer date
4. 峨山: add 27日 row, add 高清盒 column, update summary tags
5. 加盟: add 27日 row, add 88会员/29小福袋 columns, update summary tags
6. 京东: add 27日 row, add 笔记本电脑/88会员年包/88会员 columns, update summary tags
7. 新平: add 27日 row, add 碎屏险/88会员年包/集团V网 columns, update summary tags
8. Grand total table
"""
import re

with open('/home/ubuntu/gh-pages/各门店报量看板.html.bak', 'r', encoding='utf-8') as f:
    html = f.read()

# =============================================
# 1. Text replacements
# =============================================
html = html.replace('7月26日报量已更新', '7月27日报量已更新')
html = html.replace('更新于 2026-07-22', '更新于 2026-07-28')
html = html.replace('数据更新于 2026-07-26', '数据更新于 2026-07-28')

# =============================================
# Helper: parse a store's day-table
# =============================================
def parse_day_table(table_html):
    """Return (cols, entries) where entries is list of (date_str, {col: val})."""
    hm = re.search(r'<tr><th>日期</th>(.*?)</tr>', table_html)
    cols = [m.group(1) for m in re.finditer(r'<th>([^<]+)</th>', hm.group(1))]
    entries = []
    for rm in re.finditer(r'<tr><td>(\d+)日</td>(.*?)</tr>', table_html, re.DOTALL):
        date = rm.group(1)
        vals = [v.replace('<td>','').replace('</td>','').strip() for v in rm.group(2).split('</td><td>')]
        entry = {}
        for i, v in enumerate(vals):
            if i < len(cols):
                entry[cols[i]] = v if v != '-' else '-'
        entries.append((date, entry))
    return cols, entries

def rebuild_table(cols, entries):
    header = '<tr><th>日期</th><th>' + '</th><th>'.join(cols) + '</th></tr>'
    rows = []
    for date, entry in entries:
        vals = []
        for c in cols:
            v = entry.get(c, '-')
            vals.append(str(v))
        rows.append(f'<tr><td>{date}日</td><td>' + '</td><td>'.join(vals) + '</td></tr>')
    return '<table class="day-table">\n' + header + '\n' + '\n'.join(rows) + '\n</table>'

def get_sums(cols, entries):
    sums = {c: 0 for c in cols}
    for date, entry in entries:
        for c in cols:
            v = entry.get(c, '-')
            if v != '-' and str(v).isdigit():
                sums[c] += int(v)
    return sums

def replace_table_at(html, marker, new_table_html):
    """Find the table after marker and replace it."""
    idx = html.find(marker)
    if idx == -1:
        print(f"  Marker '{marker}' not found!")
        return html
    chunk = html[idx:]
    m = re.search(r'<table class="day-table">.*?</table>', chunk, re.DOTALL)
    if not m:
        print(f"  Table not found after '{marker}'!")
        return html
    old = m.group(0)
    return html.replace(old, new_table_html)

# =============================================
# 峨山店
# =============================================
print("=== 峨山店 ===")
tables = list(re.finditer(r'<table class="day-table">.*?</table>', html, re.DOTALL))
cols0, entries0 = parse_day_table(tables[0].group(0))
print(f"Original cols: {cols0}")

# Add 高清盒 column after 高清盒续费
if '高清盒' not in cols0:
    ins_idx = cols0.index('高清盒续费') + 1
    cols0.insert(ins_idx, '高清盒')

# Add 碎屏险 at end
if '碎屏险' not in cols0:
    cols0.append('碎屏险')

# Add 27日 data
entries0.append(('27', {
    '开户': '2', '高清盒': '1', '58畅享包': '1',
    '宽带': '10', '路由器': '9', '安全管家仿诈': '3'
}))

new_table = rebuild_table(cols0, entries0)
html = replace_table_at(html, '<!-- 峨山店 -->', new_table)

# Update summary tags - incrementally update specific values
# Original: 📋开户 60 → 62 (+2), 全球通宽带 178 → 188 (+10), 路由器 171 → 180 (+9)
#          安全管家仿诈 33 → 36 (+3), add 高清盒 1
# Use exact string replacements
def inc_tag(html, marker, tag_text, increment):
    """Increment a summary tag value."""
    old_val = int(re.search(rf'{re.escape(tag_text)}\s*(\d+)', html).group(1))
    new_val = old_val + increment
    html = html.replace(f'{tag_text} {old_val}', f'{tag_text} {new_val}')
    print(f"  {tag_text}: {old_val} → {new_val}")
    return html

# First find 峨山 summary row and do targeted updates
idx = html.find('<!-- 峨山店 -->')
chunk = html[idx:idx+5000]
sm = re.search(r'(<div class="summary-row">)(.*?)(</div>\s*<div class="sc-wrap">)', chunk, re.DOTALL)
old_summary = sm.group(0)

# Parse original tags from this section
original_tags_html = sm.group(2)
pairs = re.findall(r'<span class="summary-tag[^"]*">([^<]+?)</span>', original_tags_html)

# Build new tags with updated values
new_pairs = []
for p in pairs:
    parts = p.strip().rsplit(' ', 1)
    if len(parts) == 2 and parts[1].isdigit():
        label = parts[0]
        val = int(parts[1])
        
        # Apply updates
        if label == '📋开户':
            val += 2
        elif label == '全球通宽带':
            val += 10
        elif label == '路由器':
            val += 9
        elif label == '安全管家仿诈':
            val += 3
        elif label == '碎屏险':
            val += 0  # keep old value
            
        new_pairs.append((label, val))
    else:
        new_pairs.append((p.strip(), None))

# Add 高清盒
new_pairs.append(('高清盒', 1))

# Build new HTML
tag_htmls = []
for label, val in new_pairs:
    if val is None:
        tag_htmls.append(f'<span class="summary-tag">{label}</span>')
    elif val > 0:
        cls = 'summary-tag'
        if '手机' in label: cls += ' s-phone'
        if '开户' in label: cls += ' s-open'
        if '宽带' in label: cls += ' s-broad'
        tag_htmls.append(f'<span class="{cls}">{label} {val}</span>')

new_summary = sm.group(1) + '\n' + '\n'.join(tag_htmls) + '\n' + sm.group(3)
html = html.replace(old_summary, new_summary)
print("  ✅峨山 summary tags updated")

# =============================================
# 加盟厅
# =============================================
print("=== 加盟厅 ===")
tables = list(re.finditer(r'<table class="day-table">.*?</table>', html, re.DOTALL))
cols1, entries1 = parse_day_table(tables[1].group(0))
print(f"Original cols: {cols1}")

if '88会员' not in cols1:
    cols1.append('88会员')
if '29小福袋' not in cols1:
    cols1.append('29小福袋')

entries1.append(('27', {
    '开户': '4', '手机': '2', '轻合约+碎屏险': '1', '29小福袋': '1',
    '畅享包': '1', '88会员': '5', '短信免打扰': '5', '高频防骚扰': '5'
}))

new_table1 = rebuild_table(cols1, entries1)
html = replace_table_at(html, '<!-- 加盟厅 -->', new_table1)

# Update 加盟 summary tags
idx = html.find('<!-- 加盟厅 -->')
chunk = html[idx:idx+5000]
sm = re.search(r'(<div class="summary-row">)(.*?)(</div>\s*<div class="sc-wrap">)', chunk, re.DOTALL)
old_sm = sm.group(0)
pairs = re.findall(r'<span class="summary-tag[^"]*">([^<]+?)</span>', sm.group(2))

# Recompute from day-table data for 加盟
sums1 = get_sums(cols1, entries1)
print(f"加盟 sums: {{k:v for k,v in sums1.items() if v>0}}")

# Build new summary tags from computed data
jm_labels = [
    '📱手机', '📋开户', '轻合约+碎屏险', '集团V网', '电视续费包年',
    '畅享包', '平板', '短信免打扰', '高频防骚扰', '88会员', '29小福袋', '电饭煲'
]
tag_htmls = []
for lbl in jm_labels:
    # Find matching column name
    col_name = None
    for c in cols1:
        if '手机' in lbl and c == '手机':
            col_name = c
            break
        # Map properly
    if '手机' == lbl.replace('📱', ''):
        col_name = '手机'
    elif '开户' == lbl.replace('📋', ''):
        col_name = '开户'
    elif lbl == '轻合约+碎屏险':
        col_name = '轻合约+碎屏险'
    elif lbl == '集团V网':
        col_name = '集团V网'
    elif lbl == '电视续费包年':
        col_name = '电视续费包年'
    elif lbl == '畅享包':
        col_name = '畅享包'
    elif lbl == '平板':
        col_name = '平板'
    elif lbl == '短信免打扰':
        col_name = '短信免打扰'
    elif lbl == '高频防骚扰':
        col_name = '高频防骚扰'
    elif lbl == '88会员':
        col_name = '88会员'
    elif lbl == '29小福袋':
        col_name = '29小福袋'
    elif lbl == '电饭煲':
        col_name = '电饭煲'
    
    if col_name and col_name in sums1 and sums1[col_name] > 0:
        cls = 'summary-tag'
        if '手机' in lbl: cls += ' s-phone'
        if '开户' in lbl: cls += ' s-open'
        if '宽带' in lbl: cls += ' s-broad'
        tag_htmls.append(f'<span class="{cls}">{lbl} {sums1[col_name]}</span>')

new_sm = sm.group(1) + '\n' + '\n'.join(tag_htmls) + '\n' + sm.group(3)
html = html.replace(old_sm, new_sm)
print("  ✅加盟 summary tags updated")

# =============================================
# 京东店
# =============================================
print("=== 京东店 ===")
tables = list(re.finditer(r'<table class="day-table">.*?</table>', html, re.DOTALL))
cols2, entries2 = parse_day_table(tables[2].group(0))
print(f"Original cols: {cols2}")

if '笔记本电脑' not in cols2:
    cols2.append('笔记本电脑')
if '88会员年包' not in cols2:
    cols2.append('88会员年包')
if '88会员' not in cols2:
    cols2.append('88会员')

entries2.append(('27', {
    '手机': '1', '笔记本电脑': '1', '学生证': '1',
    '开户': '1', '39元开户': '2', '88会员年包': '9', '88会员': '9',
    '短信免打扰': '3', '高频防骚扰': '4'
}))

new_table2 = rebuild_table(cols2, entries2)
html = replace_table_at(html, '<!-- 京东店 -->', new_table2)

# Update 京东 summary tags
idx = html.find('<!-- 京东店 -->')
chunk = html[idx:idx+5000]
sm = re.search(r'(<div class="summary-row">)(.*?)(</div>\s*<div class="sc-wrap">)', chunk, re.DOTALL)
old_sm = sm.group(0)

sums2 = get_sums(cols2, entries2)
print(f"京东 sums: {{k:v for k,v in sums2.items() if v>0}}")

mobile_total2 = sums2.get('手机', 0) + sums2.get('轻合约+手机', 0)
open_total2 = sums2.get('开户', 0) + sums2.get('9元开户', 0) + sums2.get('39元开户', 0) + sums2.get('59元开户', 0)

jd_labels = [
    ('📱手机（含轻合约）', mobile_total2),
    ('📋开户（含9/39/59元）', open_total2),
    ('轻合约+手机', sums2.get('轻合约+手机', 0)),
    ('单独手机', sums2.get('手机', 0)),
    ('畅享包', sums2.get('畅享包', 0)),
    ('集团V网', sums2.get('集团V网', 0)),
    ('智能手表', sums2.get('智能手表', 0)),
    ('学生证', sums2.get('学生证', 0)),
    ('短信免打扰', sums2.get('短信免打扰', 0)),
    ('高频防骚扰', sums2.get('高频防骚扰', 0)),
    ('平板', sums2.get('平板', 0)),
    ('小天才手表', sums2.get('小天才手表', 0)),
    ('空气炸锅', sums2.get('空气炸锅', 0)),
    ('笔记本电脑', sums2.get('笔记本电脑', 0)),
    ('88会员年包', sums2.get('88会员年包', 0)),
    ('88会员', sums2.get('88会员', 0)),
]

tag_htmls = []
for lbl, val in jd_labels:
    if val > 0:
        cls = 'summary-tag'
        if '手机' in lbl: cls += ' s-phone'
        if '开户' in lbl: cls += ' s-open'
        if '宽带' in lbl: cls += ' s-broad'
        tag_htmls.append(f'<span class="{cls}">{lbl} {val}</span>')

new_sm = sm.group(1) + '\n' + '\n'.join(tag_htmls) + '\n' + sm.group(3)
html = html.replace(old_sm, new_sm)
print("  ✅京东 summary tags updated")

# =============================================
# 新平外呼组
# =============================================
print("=== 新平外呼组 ===")
tables = list(re.finditer(r'<table class="day-table">.*?</table>', html, re.DOTALL))
cols3, entries3 = parse_day_table(tables[3].group(0))
print(f"Original cols: {cols3}")

if '碎屏险' not in cols3:
    cols3.append('碎屏险')
if '88会员年包' not in cols3:
    cols3.append('88会员年包')
if '集团V网' not in cols3:
    cols3.append('集团V网')

entries3.append(('27', {
    '新开户': '3', '手机': '1', '碎屏险': '2', '电子学生证': '1', '视频彩铃PLUS': '8',
    '电饭煲/空气炸锅': '3', '升档大促': '2', '宽带升千': '10', '88会员年包': '35',
    '电视续费': '1', '全球通宽带': '4', 'WiFi': '4', '集团V网': '3'
}))

new_table3 = rebuild_table(cols3, entries3)
idx3 = html.find('📞 新平外呼组')
html = replace_table_at(html, '📞 新平外呼组', new_table3)

# Update 新平 summary tags
idx = html.find('📞 新平外呼组')
chunk = html[idx:idx+6000]
sm = re.search(r'(<div class="summary-row">)(.*?)(</div>\s*<table class="day-table">)', chunk, re.DOTALL)
if not sm:
    sm = re.search(r'(<div class="summary-row">)(.*?)(</div>\s*\n<table class="day-table">)', chunk, re.DOTALL)
if not sm:
    sm = re.search(r'(<div class="summary-row">)(.*?)(</div>)', chunk, re.DOTALL)

if sm:
    old_sm = sm.group(0)
    sums3 = get_sums(cols3, entries3)
    print(f"新平 sums: {sums3}")
    
    xp_labels = [
        ('新开户', sums3.get('新开户', 0)),
        ('畅享包', sums3.get('畅享包', 0)),
        ('📱手机', sums3.get('手机', 0)),
        ('电子学生证', sums3.get('电子学生证', 0)),
        ('儿童手表', sums3.get('儿童手表', 0)),
        ('29手机福袋', sums3.get('29手机福袋', 0)),
        ('9.9亲情守护', sums3.get('9.9亲情守护', 0)),
        ('视频彩铃PLUS', sums3.get('视频彩铃PLUS', 0)),
        ('电视续费', sums3.get('电视续费', 0)),
        ('升档大促', sums3.get('升档大促', 0)),
        ('宽带升千', sums3.get('宽带升千', 0)),
        ('全球通宽带', sums3.get('全球通宽带', 0)),
        ('WiFi', sums3.get('WiFi', 0)),
        ('电饭煲/空气炸锅', sums3.get('电饭煲/空气炸锅', 0)),
        ('碎屏险', sums3.get('碎屏险', 0)),
        ('88会员年包', sums3.get('88会员年包', 0)),
        ('集团V网', sums3.get('集团V网', 0)),
    ]
    tag_htmls = []
    for lbl, val in xp_labels:
        if val > 0:
            cls = 'summary-tag'
            if '手机' in lbl: cls += ' s-phone'
            if '开户' in lbl: cls += ' s-open'
            if '宽带' in lbl: cls += ' s-broad'
            tag_htmls.append(f'<span class="{cls}">{lbl} {val}</span>')
    
    new_sm = sm.group(1) + '\n' + '\n'.join(tag_htmls) + '\n' + sm.group(3)
    html = html.replace(old_sm, new_sm)
    print("  ✅新平 summary tags updated")
else:
    print("  ERROR: Could not find 新平 summary-row section")
    print(f"  Around pos {idx}: ...{html[idx:idx+200]}...")

# =============================================
# Grand Total table
# =============================================
print("=== Grand Total ===")

# Re-parse summary tags
def get_tags_around(html, marker):
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

e_t = get_tags_around(html, '<!-- 峨山店 -->')
jm_t = get_tags_around(html, '<!-- 加盟厅 -->')
jd_t = get_tags_around(html, '<!-- 京东店 -->')
xp_t = get_tags_around(html, '📞 新平外呼组')

print(f"Eshan: {e_t}")
print(f"Jiameng: {jm_t}")
print(f"Jingdong: {jd_t}")
print(f"Xinping: {xp_t}")

def upd_grand(html, key_text, e, jm, jd, xp):
    total = e + jm + jd + xp
    escaped = re.escape(key_text)
    pattern = rf'<tr><td>[^<]*?{escaped}[^<]*?</td><td[^>]*?>([^<]+)</td><td[^>]*?>([^<]+)</td><td[^>]*?>([^<]+)</td><td[^>]*?>([^<]+)</td><td[^>]*?>([^<]+)</td></tr>'
    m = re.search(pattern, html)
    if m:
        old = m.group(0)
        prefix = re.search(rf'(<tr><td>[^<]*?{escaped}[^<]*?</td>)', old).group(1)
        def fv(v): return str(v) if v else '-'
        new = f'{prefix}<td style="color:#1565c0">{fv(e)}</td><td style="color:#7b1fa2">{fv(jm)}</td><td style="color:#2e7d32">{fv(jd)}</td><td style="color:#e65100">{fv(xp)}</td><td style="background:#e3f2fd;font-weight:700">{total}</td></tr>'
        html = html.replace(old, new)
        print(f"  {key_text}: {e}/{jm}/{jd}/{xp} = {total}")
    else:
        print(f"  WARNING: '{key_text}' not found")
    return html

html = upd_grand(html, '手机（含合约）', e_t.get('📱手机',0), jm_t.get('📱手机',0), jd_t.get('📱手机（含轻合约）',0), xp_t.get('📱手机',0))
html = upd_grand(html, '开户', e_t.get('📋开户',0), jm_t.get('📋开户',0), jd_t.get('📋开户（含9/39/59元）',0), xp_t.get('新开户',0))
html = upd_grand(html, '学生证', e_t.get('电子学生证',0), 0, jd_t.get('学生证',0), 0)
html = upd_grand(html, '小福袋', e_t.get('29小福袋',0), jm_t.get('29小福袋',0), 0, xp_t.get('29手机福袋',0))
html = upd_grand(html, '轻合约', 0, jm_t.get('轻合约+碎屏险',0), jd_t.get('轻合约+手机',0), 0)
html = upd_grand(html, '视频彩铃', e_t.get('视频彩铃plus',0), 0, 0, xp_t.get('视频彩铃PLUS',0))
jm_mdr = jm_t.get('短信免打扰',0) + jm_t.get('高频防骚扰',0)
jd_mdr = jd_t.get('短信免打扰',0) + jd_t.get('高频防骚扰',0)
html = upd_grand(html, '免打扰/防骚扰', 0, jm_mdr, jd_mdr, 0)
e_tv = e_t.get('机顶盒',0)+e_t.get('机顶盒包年',0)+e_t.get('高清盒包年',0)+e_t.get('高清盒续费',0)+e_t.get('高清盒',0)
html = upd_grand(html, '电视/机顶盒', e_tv, jm_t.get('电视续费包年',0), 0, xp_t.get('电视续费',0))
html = upd_grand(html, '宽带升千', 0, 0, 0, xp_t.get('宽带升千',0))
html = upd_grand(html, '全球通宽带', e_t.get('全球通宽带',0), 0, 0, xp_t.get('全球通宽带',0))
html = upd_grand(html, 'WiFi', 0, 0, 0, xp_t.get('WiFi',0))

# =============================================
# Write
# =============================================
with open('/home/ubuntu/gh-pages/各门店报量看板.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("\n=== DONE ===")
