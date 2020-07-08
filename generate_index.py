# coding:utf-8
import os
"""
根据目录下已有的扫描文件，生成一个汇总html文件
"""

before_content="""
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<title>Converity每日扫描结果汇总</title>
</head>
<body bgcolor="#FFFFFF" text="#000000" link="#37598D" vlink="#5685AB">
<p style="font-size:24px">Converity每日扫描结果汇总</p>
</body>
<table cellPadding="8" summary="defects">
<tr bgColor="#4682B4">
<td>日期</td>
<td>过滤后的结果</td>
<td>converity扫描结果</td>
</tr>
"""

after_content="""
</table>
</html>
"""

def pdbdebug():
    import pdb
    pdb.set_trace()

# 获取某文件所有的行
def get_all_lines(file_path):
    lines = []
    f = open(file_path, 'r')    
    lines = f.readlines()
    f.close()
    return lines

# 为某一个目录生成一段html
def get_html_lines_for_dir(dir_name):
    lines = []
    lines.append("""<tr bgcolor="#F8F8F2" class="bodytextlarge">""")
    lines.append("<td>" + dir_name + "</td>")
    # 生成过滤后的错误td
    lines.append("<td>")
    lines.append("<a href=\"" + dir_name + "/tmp_index.html\">点击修复错误</a></br>")
    filter_lines = get_all_lines(dir_name + "/error_sum_filtered")
    for each in filter_lines:
        lines.append(each + "</br>")    
    lines.append("</td>")

    # 生成过滤前的错误td
    lines.append("<td>")
    lines.append("<a href=\"" + dir_name + "/index.html\">点击修复错误</a></br>")
    before_filter_lines = get_all_lines(dir_name + "/error_sum")
    for each in before_filter_lines:
        lines.append(each + "</br>")
    lines.append("</td>")

    lines.append("</tr>")

    return lines

final_file = open('index.html', 'w')
final_file.writelines([before_content])
# 遍历每个目录，为每个目录生成一段 html td 代码并写入
all_dirs = next(os.walk("."))[1]
for each_dir in list(reversed(sorted(all_dirs))):
    final_file.writelines(get_html_lines_for_dir(each_dir))
final_file.writelines([after_content])

print('Finish filtering converity errors!!')