#!/usr/bin/env python3
"""
Update 各门店报量看板.html with July 27 data - v2 with precise position-based updates.
"""
import re

with open('/home/ubuntu/gh-pages/各门店报量看板.html.bak', 'r', encoding='utf-8') as f:
    html = f.read()

# =============================================
# 1. Update notice bar and header dates
# =============================================
html = html.replace('7月26日报量已更新', '7月27日报量已更新')
html = html.replace('更新于 2026-07-22', '更新于 2026-07-28')
html = html.replace('数据更新于 2026-07-26', '数据更新于 2026-07-28')

# =============================================
# Helper: Find table by position index
# =============================================
tables = list(re.finditer(r'<table class="day-table">.*?</table>', html, re.DOTALL))
# Table 0 = 峨山, Table 1 = 加盟, Table 2 = 京东, Table 3 = 新平

def get_table_cols(table_idx):
    t = tables[table_idx]
    hm = re.search(r'<tr><th>日期</th>(.*?)</tr>', t.group(0))
    if not hm:
        return []
    cols = []
    for p in hm.group(1).split('</th><th>'):
        c = p.replace('<th>','').replace('</th>','').strip()
        if c: cols.append(c)
    return cols

def get_table_sums(table_idx):
    """Return {col_name: sum} for the table."""
    t = tables[table_idx]
    table_html = t.group(0)
    cols = get_table_cols(table_idx)
    sums = {c: 0 for c in cols}
    for row_m in re.finditer(r'<tr><td>(\d+)日</td>(.*?)</tr>', table_html, re.DOTALL):
        vals = [v.strip() for v in row_m.group(2).split('</td><td>')]
        vals = [v.replace('<td>','').replace('</td>','').strip() for v in vals]
        for i, v in enumerate(vals):
            if i < len(cols) and v.isdigit():
                sums[cols[i]] += int(v)
    return sums

def add_column_to_table(table_idx, col_name, after_col=None):
    """Add a new column to table header and all existing rows. Updates the global html."""
    global html, tables
    t = tables[table_idx]
    old_table = t.group(0)
    cols = get_table_cols(table_idx)
    
    if col_name in cols:
        return  # already exists
    
    # Add to header after specified column or at end
    header_m = re.search(r'(<tr><th>日期</th>)(.*?)(</tr>)', old_table, re.DOTALL)
    old_header = header_m.group(0)
    
    if after_col:
        new_header = old_header.replace(f'<th>{after_col}</th>', f'<th>{after_col}</th><th>{col_name}</th>')
    else:
        new_header = old_header.replace('</tr>', f'<th>{col_name}</th></tr>')
    
    new_table = old_table.replace(old_header, new_header)
    
    # Add <td>-</td> to every data row before closing </tr>
    new_table = re.sub(
        r'(<tr><td>\d+日</td>.*?)</tr>',
        r'\1<td>-</td></tr>',
        new_table
    )
    
    html = html.replace(old_table, new_table)
    tables = list(re.finditer(r'<table class="day-table">.*?</table>', html, re.DOTALL))
    print(f"  Added column '{col_name}' to table #{table_idx}")

def add_data_row(table_idx, date_str, data_map):
    """Add a data row to the table. data_map: col_name -> value or None."""
    global html, tables
    t = tables[table_idx]
    old_table = t.group(0)
    cols = get_table_cols(table_idx)
    
    vals = []
    for col in cols:
        if col in data_map:
            vals.append(str(data_map[col]))
        else:
            vals.append('-')
    
    new_row = f'<tr><td>{date_str}</td><td>' + '</td><td>'.join(vals) + '</td></tr>'
    
    # Insert before closing </table>
    new_table = old_table.rstrip() + '\n' + new_row + '\n</table>'
    html = html.replace(old_table, new_table)
    tables = list(re.finditer(r'<table class="day-table">.*?</table>', html, re.DOTALL))
    print(f"  Added {date_str} row to table #{table_idx}")

def update_summary_tags(table_idx, new_tags_map):
    """Replace summary-row content. new_tags_map: {label: value}. Uses the store card found before the table."""
    global html
    t = tables[table_idx]
    start = t.start()
    
    # Find the summary-row before this table
    chunk_before = html[max(0,start-3000):start]
    sm = re.search(r'(<div class="summary-row">)(.*?)(</div>\s*<div class="sc-wrap">)', chunk_before, re.DOTALL)
    if not sm:
        print(f"  ERROR: Could not find summary-row for table #{table_idx}")
        return
    
    old = sm.group(0)
    
    # Build new tags
    tag_htmls = []
    for label, val in new_tags_map.items():
        cls = 'summary-tag'
        if '手机' in label: cls += ' s-phone'
        if '开户' in label: cls += ' s-open'
        if '宽带' in label: cls += ' s-broad'
        tag_htmls.append(f'<span class="{cls}">{label} {val}</span>')
    
    new = sm.group(1) + '\n' + '\n'.join(tag_htmls) + '\n' + sm.group(3)
    html = html.replace(old, new)
    print(f"  Updated summary tags for table #{table_idx}")

def update_grand_row(row_key, eshan_val, jam_val, jd_val, xp_val):
    """Update a row in the grand total table."""
    global html
    total = eshan_val + jam_val + jd_val + xp_val
    escaped = re.escape(row_key)
    
    pattern = rf'<tr><td>[^<]*?{escaped}[^<]*?</td><td[^>]*?>(\d+)</td><td[^>]*?>(\d+)</td><td[^>]*?>(\d+)</td><td[^>]*?>(\d+)</td><td[^>]*?>(\d+)</td></tr>'
    m = re.search(pattern, html)
    if m:
        old = m.group(0)
        prefix = re.search(rf'(<tr><td>[^<]*?{escaped}[^<]*?</td>)', old).group(1)
        new = f'{prefix}<td style="color:#1565c0">{eshan_val}</td><td style="color:#7b1fa2">{jam_val}</td><td style="color:#2e7d32">{jd_val}</td><td style="color:#e65100">{xp_val}</td><td style="background:#e3f2fd;font-weight:700">{total}</td></tr>'
        html = html.replace(old, new)
        print(f"  Grand row '{row_key}': updated")
    else:
        print(f"  WARNING: Grand row '{row_key}' not found")

# =============================================
# TABLE 0: 峨山店
# =============================================
print("=== 峨山店 (Table 0) ===")
cols0 = get_table_cols(0)
print(f"Current columns: {cols0}")

# Add 高清盒 column (after 高清盒续费)
add_column_to_table(0, '高清盒', '高清盒续费')
add_column_to_table(0, '碎屏险', '安全管家仿诈')

# Add 27日 row: 开户2, 高清盒1, 58畅享包1, 宽带10, 路由器9, 安全管家仿诈3, 碎屏险0
add_data_row(0, '27日', {'开户': 2, '高清盒': 1, '58畅享包': 1, '宽带': 10, '路由器': 9, '安全管家仿诈': 3, '碎屏险': 0})

# Recompute sums
sums0 = get_table_sums(0)
print(f"峨山 sums: {sums0}")

# Build new summary tags (preserving static items like 和校园, 顺差碎屏险, etc.)
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
# Only include non-zero values
filtered_tags = {k: v for k, v in eshan_tags.items() if v > 0}
update_summary_tags(0, filtered_tags)

# =============================================
# TABLE 1: 加盟厅
# =============================================
print("=== 加盟厅 (Table 1) ===")
cols1 = get_table_cols(1)
print(f"Current columns: {cols1}")

# Add 88会员 and 29小福袋
add_column_to_table(1, '88会员')
add_column_to_table(1, '29小福袋')

# Add 27日 row: 开户4, 手机2, 轻合约+碎屏险1, 29小福袋1, 畅享包1, 88会员5, 短信免打扰5, 高频防骚扰5
add_data_row(1, '27日', {'开户': 4, '手机': 2, '轻合约+碎屏险': 1, '29小福袋': 1, '畅享包': 1, '88会员': 5, '短信免打扰': 5, '高频防骚扰': 5})

sums1 = get_table_sums(1)
print(f"加盟 sums: {sums1}")

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
filtered_jm = {k: v for k, v in jm_tags.items() if v > 0}
update_summary_tags(1, filtered_jm)

# =============================================
# TABLE 2: 京东店
# =============================================
print("=== 京东店 (Table 2) ===")
cols2 = get_table_cols(2)
print(f"Current columns: {cols2}")

# Add 笔记本电脑, 88会员年包, 88会员
add_column_to_table(2, '笔记本电脑')
add_column_to_table(2, '88会员年包')
add_column_to_table(2, '88会员')

# Add 27日 row: 手机1, 笔记本电脑1, 学生证1, 开户1, 39元开户2, 88会员年包9, 88会员9, 短信免打扰3, 高频防骚扰4
add_data_row(2, '27日', {'手机': 1, '笔记本电脑': 1, '学生证': 1, '开户': 1, '39元开户': 2, '88会员年包': 9, '88会员': 9, '短信免打扰': 3, '高频防骚扰': 4})

sums2 = get_table_sums(2)
print(f"京东 sums: {sums2}")

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
filtered_jd = {k: v for k, v in jd_tags.items() if v > 0}
update_summary_tags(2, filtered_jd)

# =============================================
# TABLE 3: 新平外呼组
# =============================================
print("=== 新平外呼组 (Table 3) ===")
cols3 = get_table_cols(3)
print(f"Current columns: {cols3}")

# Add 碎屏险, 88会员年包, 集团V网
# Insert after 电子学生证 since that makes the most sense
add_column_to_table(3, '碎屏险')
add_column_to_table(3, '88会员年包')
add_column_to_table(3, '集团V网')

# Add 27日 row
add_data_row(3, '27日', {
    '新开户': 3, '手机': 1, '碎屏险': 2, '电子学生证': 1, '视频彩铃PLUS': 8,
    '电饭煲/空气炸锅': 3, '升档大促': 2, '宽带升千': 10, '88会员年包': 35,
    '电视续费': 1, '全球通宽带': 4, 'WiFi': 4, '集团V网': 3
})

sums3 = get_table_sums(3)
print(f"新平 sums: {sums3}")

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
filtered_xp = {k: v for k, v in xp_tags.items() if v > 0}
update_summary_tags(3, filtered_xp)

# =============================================
# 6. Update grand total table
# =============================================
print("=== Grand Total Table ===")

# Parse all store tags from summary sections
def parse_summary_around_table(table_idx):
    """Parse summary tags from the summary-row before a table."""
    t = tables[table_idx]
    chunk = html[max(0,t.start()-3000):t.start()]
    sm = re.search(r'<div class="summary-row">(.*?)</div>', chunk, re.DOTALL)
    if not sm: return {}
    pairs = re.findall(r'<span class="summary-tag[^"]*">([^<]+?)</span>', sm.group(1))
    tags = {}
    for p in pairs:
        parts = p.strip().rsplit(' ', 1)
        if len(parts) == 2 and parts[1].isdigit():
            tags[parts[0]] = int(parts[1])
    return tags

eshan_t = parse_summary_around_table(0)
jm_t = parse_summary_around_table(1)
jd_t = parse_summary_around_table(2)
xp_t = parse_summary_around_table(3)

print(f"Eshan: {eshan_t}")
print(f"Jiameng: {jm_t}")
print(f"Jingdong: {jd_t}")
print(f"Xinping: {xp_t}")

# 手机（含合约）
update_grand_row('手机（含合约）',
    eshan_t.get('📱手机', 0),
    jm_t.get('📱手机', 0),
    jd_t.get('📱手机（含轻合约）', 0),
    xp_t.get('📱手机', 0))

# 开户
update_grand_row('开户',
    eshan_t.get('📋开户', 0),
    jm_t.get('📋开户', 0),
    jd_t.get('📋开户（含9/39/59元）', 0),
    xp_t.get('新开户', 0))

# 学生证
update_grand_row('学生证',
    eshan_t.get('电子学生证', 0), 0,
    jd_t.get('学生证', 0), 0)

# 小福袋
update_grand_row('小福袋',
    eshan_t.get('29小福袋', 0),
    jm_t.get('29小福袋', 0), 0,
    xp_t.get('29手机福袋', 0))

# 轻合约
update_grand_row('轻合约', 0,
    jm_t.get('轻合约+碎屏险', 0),
    jd_t.get('轻合约+手机', 0), 0)

# 视频彩铃
update_grand_row('视频彩铃',
    eshan_t.get('视频彩铃plus', 0), 0, 0,
    xp_t.get('视频彩铃PLUS', 0))

# 免打扰/防骚扰
jm_mdr = jm_t.get('短信免打扰', 0) + jm_t.get('高频防骚扰', 0)
jd_mdr = jd_t.get('短信免打扰', 0) + jd_t.get('高频防骚扰', 0)
update_grand_row('免打扰/防骚扰', 0, jm_mdr, jd_mdr, 0)

# 电视/机顶盒
eshan_tv = eshan_t.get('机顶盒', 0) + eshan_t.get('机顶盒包年', 0) + eshan_t.get('高清盒包年', 0) + eshan_t.get('高清盒续费', 0) + eshan_t.get('高清盒', 0)
jm_tv = jm_t.get('电视续费包年', 0)
xp_tv = xp_t.get('电视续费', 0)
update_grand_row('电视/机顶盒', eshan_tv, jm_tv, 0, xp_tv)

# 宽带升千
update_grand_row('宽带升千', 0, 0, 0, xp_t.get('宽带升千', 0))

# 全球通宽带
update_grand_row('全球通宽带',
    eshan_t.get('全球通宽带', 0), 0, 0,
    xp_t.get('全球通宽带', 0))

# WiFi
update_grand_row('WiFi', 0, 0, 0, xp_t.get('WiFi', 0))

# =============================================
# Write output
# =============================================
with open('/home/ubuntu/gh-pages/各门店报量看板.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("\n=== DONE ===")
