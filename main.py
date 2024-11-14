from datetime import datetime, timedelta
from urllib.parse import urlencode
from bs4 import BeautifulSoup
import requests
import json
import os
import re





BOTTOKEN = os.environ.get('BOTTOKEN')
USERID = os.environ.get('USERID')
UA = os.environ.get('UA')
COOKIE = os.environ.get('COOKIE')














whitelist_url= 'https://github.com/ayyayyayy2002/BilibiliAutoReport/blob/main/%E4%BA%91%E7%AB%AF%E6%96%87%E4%BB%B6/whitelist.txt'
log_file = f"{(datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d %H-%M-%S')}.txt"
keyword_file = 'keywords.txt'
uid_file = 'uid.txt'
keywords = []
uids = set()
offset= ''
with open(log_file, "w", encoding='utf-8') as file:
    file.write((datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S'))
with open(keyword_file, 'r', encoding='utf-8') as f:
    for line in f:
        stripped_line = line.strip()
        if stripped_line and not stripped_line.startswith('#'):  # 排除空行和以“#”开头的行
            keywords.append(stripped_line)

for keyword in keywords:

    base_url = 'https://search.bilibili.com/video?'
    search_params_list = [

        {
            'keyword': keyword,
            'from_source': 'video_tag',
            'order': 'pubdate'
        }

    ]

    for search_params in search_params_list:
        search_url = base_url + urlencode(search_params)
        print(search_url)

        try:
            # 添加头部信息
            headers = {'User-Agent': UA,}
            response = requests.get(search_url, headers=headers, timeout=(5, 10))
            response.raise_for_status()  # 检查请求是否成功
            soup = BeautifulSoup(response.text, 'html.parser')
            count = 0  # 计数器，用于限制获取的UID数量
            for link in soup.select('.bili-video-card .bili-video-card__info--owner'):
                if count >= 1:
                    break
                href = link['href']
                uid = href.split('/')[-1]
                uids.add(uid)
                count += 1

        except requests.exceptions.RequestException as e:
            print(f"关键词 \"{keyword}\" 搜索页面请求失败：", e)
#print(uids)
try:
    response = requests.get(whitelist_url)

    for line in response.text.split('\n'):
        uid = line.strip()
        if uid:  # 确保 uid 不为空
            uids.add(uid)

except Exception as e:
    print(e)


for uid in uids:
    offset=''
    reportcount=0
    try:
        while True:
            dyids = set()
            get_dy_url=f'https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/all?offset={offset}&host_mid={uid}'
            headers = {'User-Agent': UA,'cookie':COOKIE}
            response = requests.get(get_dy_url, headers=headers, timeout=(5, 10))
            #print(response.text)
            data = json.loads(response.text)
            #print(response.text)
            for item in data['data']['items']:
                dyids.add(item['id_str'])
            for item in data :
                offset = data['data']['offset']
            print('uid:',uid,'offset:',offset)

            for dyid in dyids:

                try:
                    dyids = set()
                    report_url = 'https://api.bilibili.com/x/dynamic/feed/dynamic_report/add'
                    headers = {'cookie': COOKIE,'User-Agent': UA}
                    params = {'csrf': re.search(r'bili_jct=([^;]*)', COOKIE).group(1),}
                    json_data = {
                        'accused_uid': int(uid),
                        'dynamic_id': dyid,
                        'reason_type': 0,
                        'reason_desc': '侮辱国家领导人，宣扬台独反华内容。审核结果：下架此视频并永久封禁该账号',
                    }
                    response = requests.post(report_url, params=params,headers=headers,json=json_data, timeout=(5, 10))
                    reportcount=reportcount+1
                    print(f"{uid},{response.text},{reportcount}")
                    if reportcount % 10 == 1:
                        with open(log_file, "a", encoding='utf-8') as file:
                            file.write(f"\n{uid},{response.text},{reportcount}")
                except requests.exceptions.RequestException as e:
                    print(e)


            if  offset == '' or reportcount > 30:
                break

    except requests.exceptions.RequestException as e:
        print(e)

with open(log_file, "a", encoding='utf-8') as file:
    file.write(f"\n{(datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')}")

if USERID:
    with open(log_file, 'r', encoding='utf-8') as file:
        content = file.read()  # 读取文件内容

    # 发送消息到 Telegram
    url = f'https://api.telegram.org/bot{BOTTOKEN}/sendDocument'
    payload = {'chat_id': USERID,}
    files = {'document': (log_file, content.encode(), 'text/plain')}
    response = requests.post(url, data=payload, files=files)
else:
    exit(0)
