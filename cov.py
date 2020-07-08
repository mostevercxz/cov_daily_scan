# coding:utf-8
import re
import shutil
"""Python2 自带的 html parser 太弱,为了不依赖三方库,自己进行逐行解析
解析规则:
1. 正则匹配形如 <td>108</td> 这样的行
2. 从该行开始解析,解析接下来的4行，用 id 作为 key,插入到 dict 中
"""

# 已确认不需要处理的文件(通配符)列表
# 去掉 protobuf/repeated_field.h 错误
# 去掉 c++/6.3.0 错误
# 去掉所有 log4cxx 错误
confirm_ok_file_list = [
    'protobuf/repeated_field.h',
    'c++/6.3.0',
    'thirdpart/include/log4cxx/'    
]

# 已确认不需要处理的函数列表
confirm_ok_function_list = [    
    ['Cmd::Super::t_Super2SceneInvitCodeInfo::t_Super2SceneInvitCodeInfo()',                   'UNINIT_CTOR'],
    ['Cmd::Info::t_Country_OnlineNum::t_Country_OnlineNum()',                                  'UNINIT_CTOR'],
    ['Cmd::Sound::t_SendNewGameUserInfo::t_SendNewGameUserInfo()',                             'UNINIT_CTOR'],
    ['FunctionTimes::FunctionTimes(int, char const *)',                                        'UNINIT_CTOR'],
    ['Cmd::Scene::t_fresh_MapIndex::t_fresh_MapIndex()',                                       'UNINIT_CTOR'],
    ['Cmd::Super::t_ResponseLoginTask_SuperGate::t_ResponseLoginTask_SuperGate()',             'UNINIT_CTOR'],
    ['Cmd::Super::t_SceneRetBalanceInfo::t_SceneRetBalanceInfo()',                             'UNINIT_CTOR'],
    ['Cmd::Moni::t_sendServerListCmd::t_sendServerListCmd()',                                  'UNINIT_CTOR'],
    ['ImagePassportManager::ImagePassportManager()',                                           'UNINIT_CTOR'],
    ['Cmd::Super::t_CountryInfo_Session::t_CountryInfo_Session()',                             'UNINIT_CTOR'],
    ['Cmd::Sound::t_SendCountryInfo::t_SendCountryInfo()',                                     'UNINIT_CTOR'],
    ['Cmd::stIphoneRequestLoginCmd::stIphoneRequestLoginCmd()',                                'UNINIT_CTOR'],
    ['SprConfig::SprConfig()',                                                                 'UNINIT_CTOR'],
    ['Cmd::Sound::t_SendCountryInfo_1::t_SendCountryInfo_1()',                                 'UNINIT_CTOR'],
    ['FunctionTimesV2::FunctionTimesV2(char const *, unsigned long const &amp;)',              'UNINIT_CTOR'],
    ['Cmd::Super::t_Startup_ServerEntry_NotifyMe::t_Startup_ServerEntry_NotifyMe()',           'UNINIT_CTOR'],
    ['FunctionUser::save()::ReadData::ReadData()',                                             'UNINIT_CTOR'],
    ['FunctionUser::readFunctionCharbase()::ReadData::ReadData()',                             'UNINIT_CTOR'],
    ['zRegex::zRegex()',                                                                       'UNINIT_CTOR'],
    ['FunctionTime::FunctionTime(unsigned long, char const *, char const *, int)',             'UNINIT_CTOR'],
    ['CommandTime::CommandTime(unsigned long, char const *, unsigned char, unsigned char)',    'UNINIT_CTOR'],
    ['FunctionTimes::FunctionTimes(int, char const *)',                                        'UNINIT_CTOR'],
    ['ServerTask::msgParse_Startup(Cmd::t_NullCmd const *, unsigned int)',                     'SWAPPED_ARGUMENTS'],
    ['SceneNpc::~SceneNpc()',                                                                  'UNCAUGHT_EXCEPT']
]

class OneCoverityError(object):
    def __init__(self, id, idline, typeline,fileline,contentline,classifyline):
        self.id = id
        self.idline = idline
        self.typeline = typeline
        self.fileline = fileline
        self.contentline = contentline
        self.classifyline = classifyline

    # 返回 True 代表这个错误已经被确认过,不需要再显示出来
    def is_confirm_ok(self):
        # 去掉所有 CHECKED_RETURN 类型的错误
        if self.typeline.find('CHECKED_RETURN') != -1:
            return True
        
        # 按文件通配符匹配去掉错误
        for eachfile in confirm_ok_file_list:
            if self.fileline.find(eachfile) != -1:
                return True
                
        # 下面就是去掉具体的函数错误
        for eachfunc in confirm_ok_function_list:
            if self.contentline.find(eachfunc[0]) != -1 and self.typeline.find(eachfunc[1]) != -1:
                return True
        
        return False

    # 返回本错误写入文件的内容
    def get_write_lines(self, current_error_number):
        ret = []
        ret.append('<tr bgcolor="#F8F8F2" class="bodytextlarge">\n')
        ret.append('<td>' + str(current_error_number) + '</td>\n')
        ret.append(self.typeline)
        ret.append(self.fileline)
        ret.append(self.contentline)
        ret.append(self.classifyline)
        ret.append('</tr>\n')
        return ret


lines = []
converity_file = open('index.html', 'r')
lines = converity_file.readlines()
converity_file.close()

# converity 生成的错误数量汇总,key:错误类型,value:错误出现的次数
converity_error_num_dict = {}
# 过滤后的错误数量汇总
converity_filtered_error_num_dict = {}

# 遍历文件每一行，得到所有的 converity 错误列表
first_match_line_number = len(lines)
last_match_line_number = 0
error_dict = {}
pattern = re.compile("<td>([0-9]+)</td>")
i = 0
while i < len(lines):
    m = pattern.match(lines[i])    
    if m is not None:
        first_match_line_number = min(i, first_match_line_number)
        last_match_line_number  = max(i, last_match_line_number)
        id = int(m.group(1))
        error = OneCoverityError(id, lines[i],lines[i+1], lines[i+2], lines[i+3], lines[i+4])
        tmp_get = converity_error_num_dict.get(lines[i+1], None)
        if tmp_get is None:
            converity_error_num_dict[lines[i+1]] = 0
        converity_error_num_dict[lines[i+1]] = converity_error_num_dict[lines[i+1]] + 1
        if not error.is_confirm_ok():
            error_dict[id] = error
        i = i + 5
        continue
    i = i + 1

# 将过滤后的错误，重新写入网页
newfile=open('tmp_index.html', 'w')
newfile.writelines(lines[0:first_match_line_number-1])
current_error_number = 1
for each_error in error_dict.keys():
    tmp_get = converity_filtered_error_num_dict.get(error_dict[each_error].typeline, None)
    if tmp_get is None:
        converity_filtered_error_num_dict[error_dict[each_error].typeline] = 0
    converity_filtered_error_num_dict[error_dict[each_error].typeline] = converity_filtered_error_num_dict[error_dict[each_error].typeline] + 1
    newfile.writelines(error_dict[each_error].get_write_lines(current_error_number))
    current_error_number = current_error_number + 1
newfile.writelines(lines[last_match_line_number+6:len(lines)])
newfile.close()

# 生成2个错误类型数量的汇总文件,1个是过滤前，1个是过滤后
error_sum_file=open('error_sum', 'w')
error_sum_file.writelines(['Total Error:' + str(sum(converity_error_num_dict.values())) + '\n'])
for each in sorted(converity_error_num_dict.keys()):
    tmp_str = str(converity_error_num_dict[each]) + " " + each.replace("<td>", "").replace("</td>", "")
    error_sum_file.writelines([tmp_str])
error_sum_file.close()

filtered_error_sum_file=open('error_sum_filtered', 'w')
filtered_error_sum_file.writelines(['Total Error:' + str(sum(converity_filtered_error_num_dict.values())) + '\n'])
for each in sorted(converity_filtered_error_num_dict.keys()):
    tmp_str = str(converity_filtered_error_num_dict[each]) + " " + each.replace("<td>", "").replace("</td>", "")
    filtered_error_sum_file.writelines([tmp_str])
filtered_error_sum_file.close()

print('Finish filtering converity errors!!')