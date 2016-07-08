import functools
import getpass
import http.cookiejar
import json
import time
import urllib
from urllib import request, parse

import chaoxing_enc

HEADERS = {
    'User-Agent': 'Dalvik/1.6.0 (Linux; U; Android 4.1.2; sdk Build/MASTER) ChaoXingStudy_3_1.4_android_phone_5',
    'contentType': 'utf-8'
}


def login(name, pwd):
    url_base = 'http://sso.chaoxing.com/apis/login/userLogin.do'
    params = {
        'username': name,
        'password': chaoxing_enc.chaoxing_user_pwd_enc(pwd)
    }
    resp = http_request_get_with_params(url_base, params)
    json_obj = json.loads(resp)
    return json_obj['msg']


def get_subjects():
    url = chaoxing_enc.chaoxing_get_subscribe_url()
    resp = http_request_get(url)
    json_obj = json.loads(resp)
    channel_list = json_obj['channelList']
    subjects = []
    for chan in channel_list:
        if ('cataName' in chan) and (chan['cataName'] == '课程'):
            subjects.append(chan['content'])
    return subjects


def get_clazz(clazz_id):
    url = ('http://mooc1-api.chaoxing.com/gas/clazz?id=%s&fields=id,bbsid,isstart,state,isthirdaq,begindate,'
           'course.fields(id,name,imageurl,privately,teacherfactor,unfinishedJobcount,jobcount,state,knowledge.fields'
           '(id,name,indexOrder,parentnodeid,status,layer,label,begintime))&view=json') % clazz_id
    resp = http_request_get(url)
    json_obj = json.loads(resp)['data'][0]['course']['data'][0]['knowledge']['data']
    return json_obj


def get_gas_knowledge(knowledge_id):
    url = ('http://mooc1-api.chaoxing.com/gas/knowledge?id=%s&fields=begintime,clickcount,description,id,'
           'indexorder,jobUnfinishedCount,jobcount,jobfinishcount,label,layer,listPosition,name,openlock,'
           'parentnodeid,status,card.fields(cardIndex,cardorder,description,id,knowledgeTitile,knowledgeid,theme,title)'
           '.contentcard(all)&view=json') % knowledge_id
    resp = http_request_get(url)
    json_obj = json.loads(resp)
    return json_obj


def get_card_id(knowledge_id):
    json_obj = get_gas_knowledge(knowledge_id)
    cards = json_obj['data'][0]['card']['data']
    video_card = None
    for card in cards:
        if card['title'] == '视频':
            video_card = card
    return video_card['id']


def get_knowledge_marg(clazzid, courseid, knowledgeid, cardid, userid):
    url_base = 'http://mooc1-api.chaoxing.com/knowledge/marg'
    params = {
        'clazzid': clazzid,
        'courseid': courseid,
        'knowledgeid': knowledgeid,
        'cardid': cardid,
        'userid': userid,
        'view': 'json',
        'control': True
    }
    resp = http_request_get_with_params(url_base, params)
    json_obj = json.loads(resp)
    return json_obj


def get_video_info(object_id):
    url_base = 'http://mooc1-api.chaoxing.com/ananas/status/'
    url = url_base + object_id
    resp = http_request_get(url)
    json_obj = json.loads(resp)
    return json_obj


# 发出带参数的get请求
def http_request_get_with_params(url_base, params):
    url_params = parse.urlencode(params)
    url = url_base + '?' + url_params
    return http_request_get(url)


# 根据url发出get请求
def http_request_get(url):
    req = request.Request(url, headers=HEADERS,
                          method='GET')
    response = urllib.request.urlopen(req)
    resp = response.read().decode('utf-8')
    return resp


# 读取整型输入，不符合则要求重新输入
def input_int(hint, max_value):
    num = -1
    while not (0 <= num < max_value):
        while True:
            num = None
            try:
                num = int(input(hint))
            except:
                pass
            if type(num) == int:
                break
    return num


# 模拟播放视频
def play_video(dtoken, other_info, duration, job_id, clazz_id, object_id, user_id):
    interval = 10
    playing_time = 0
    first_report_url = chaoxing_enc.chaoxin_video_report_url(dtoken, other_info, playing_time, duration, job_id,
                                                             clazz_id, object_id, user_id, 3)
    http_request_get(first_report_url)
    time.sleep(interval + 5)
    playing_time += (interval + 5)
    while playing_time <= duration:
        report_url = chaoxing_enc.chaoxin_video_report_url(dtoken, other_info, playing_time, duration, job_id,
                                                           clazz_id, object_id, user_id, 0)
        http_request_get(report_url)
        print('已播放: %d / 总长: %d' % (playing_time, duration))
        time.sleep(interval)
        playing_time += interval


# 排序cmp，按照小数点分割label，靠前的数字优先排序
def clazz_info_cmp(x, y):
    x_labels = x['label'].split('.')
    y_labels = y['label'].split('.')
    for i in range(0, len(x_labels)):
        if x_labels[i] != y_labels[i]:
            return int(x_labels[i]) - int(y_labels[i])
    return 0


# cookie处理器
cj = http.cookiejar.LWPCookieJar()
cookie_support = request.HTTPCookieProcessor(cj)
opener = request.build_opener(cookie_support, request.HTTPHandler)
request.install_opener(opener)

if __name__ == '__main__':
    username = input('请输入用户名： ')
    password = getpass.getpass('请输入密码（不显示输入）： ')
    print('正在加载...')
    user_info = login(username, password)
    print('''
账户基本信息：
学校：\t\t%s
名称：\t\t%s
用户名：\t%s
电话：\t\t%s
邮箱：\t\t%s
        ''' % (user_info['schoolname'], user_info['name'], user_info['uname'], user_info['phone'], user_info['email']))
    subjects = get_subjects()
    print('课程列表：')
    for index, subject in enumerate(subjects):
        print('%d) %s' % (index, subject['course']['data'][0]['name']))
        if subject['state'] == 0:
            print('（未完成）')

    num = input_int('输入要进行刷课的课程编号： ', len(subjects))

    subject = subjects[num]
    print('正在加载...')
    clazz_info = get_clazz(subject['id'])

    # 去除分类标签
    clazz_info = [elem for elem in clazz_info if elem['layer'] != 1]

    # 根据标签排序
    clazz_info.sort(key=functools.cmp_to_key(clazz_info_cmp))
    print('\n课程内容：')
    for index, item in enumerate(clazz_info):
        print('%d) %s %s' % (index, item['label'], item['name']))

    num = input_int('输入标题编号，本工具从此开始刷课： ', len(clazz_info))
    for i in range(num, len(clazz_info)):
        knowledge = clazz_info[i]
        card_id = get_card_id(knowledge['id'])
        user_id = user_info['puid']
        marg = get_knowledge_marg(subject['id'], subject['course']['data'][0]['id'], knowledge['id'], card_id,
                                  user_id)

        defaults = marg['defaults']
        report_url = defaults['reportUrl']
        clazz_id = defaults['clazzId']
        report_time_interval = defaults['reportTimeInterval']
        attachments = marg['attachments'][0]
        object_id = attachments['objectId']
        other_info = attachments['otherInfo']
        job_id = attachments['jobid']

        video_info = get_video_info(object_id)
        dtoken = video_info['dtoken']
        duration = video_info['duration']

        print('开始模拟播放 %s %s' % (knowledge['label'], knowledge['name']))
        play_video(dtoken, other_info, duration, job_id, clazz_id, object_id, user_id)

    # 退出提示
    input('操作完成，按回车键退出')
