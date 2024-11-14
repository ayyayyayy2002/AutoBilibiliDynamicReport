from datetime import datetime, timedelta
from urllib.parse import urlencode
from bs4 import BeautifulSoup
import requests
import json
import os
import re

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
COOKIE = "buvid3=58969B5F-F8F5-EA97-7529-A2B79CFAB41958435infoc; b_nut=1725341558; _uuid=EA69105105-91038-65109-D6A7-9D761052FCBD159128infoc; buvid4=12BB76DE-76B6-9A64-1007-D8A1A1AF9B0C59065-024090305-UYUGNkqyRoU%2BT8NfnBkvwQ%3D%3D; rpdid=|(JYl~~|lRm)0J'u~klJRkYJJ; header_theme_version=CLOSE; enable_web_push=DISABLE; PVID=1; LIVE_BUVID=AUTO8617289603999361; CURRENT_FNVAL=4048; buvid_fp_plain=undefined; bp_t_offset_3494374224694043=988808970275651584; hit-dyn-v2=1; bp_t_offset_3546780807465288=989567616118947840; is-2022-channel=1; fingerprint=406b36dce4312d13996f5de36c9df3a6; bp_t_offset_3546632549305041=993240277013495808; bp_t_offset_3493274255887316=993242317122961408; DedeUserID=3546744296049110; DedeUserID__ckMd5=42fcfe05851ba49a; buvid_fp=406b36dce4312d13996f5de36c9df3a6; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MzE4MjA0MzEsImlhdCI6MTczMTU2MTE3MSwicGx0IjotMX0.skDEntE5EtSInlFzP6nZfq76rwrdWloAOPB9DdrN9xo; bili_ticket_expires=1731820371; home_feed_column=4; bp_t_offset_3546744296049110=999539001171902464; b_lsid=21010DEB109_193292A0F57; browser_resolution=1224-1094; SESSDATA=8ff7d8ba%2C1747117755%2Ceb26c%2Ab1CjB0iEGNUCwHz2nHimj0l09xGQUPH9ZhU9ASEIMuLVyHKKR8jLG4bvNobibQ_6r8aqISVmR1aHI2TU5UVmZUV2ZGaVNpSkJGTTRIX2ZTUzFOZUdpdmtmVHhLU0FwRzFqb1lCT1R5VVZ1OHFrYXV0VUZzdWo5MWkycUFUU3E0NC1IalNoMGpZVmdBIIEC; bili_jct=613df1ed5e8ad47c9305199190d83d12; sid=q1h5ummn; x-bili-gaia-vtoken=53b304ae17df4a3aa2b3d510f9964063"
os.environ['COOKIE'] = COOKIE
os.environ['UA'] = UA



BOTTOKEN = os.environ.get('BOTTOKEN')
USERID = os.environ.get('USERID')
#UA = os.environ.get('UA')
#COOKIE = os.environ.get('COOKIE')















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
                if count >= 10:
                    break
                href = link['href']
                uid = href.split('/')[-1]
                uids.add(uid)
                count += 1

        except requests.exceptions.RequestException as e:
            print(f"关键词 \"{keyword}\" 搜索页面请求失败：", e)
#print(uids)
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
                        'reason_desc': 'uishbkldfhbkdsnb zcklvb',
                    }
                    response = requests.post(report_url, params=params,headers=headers,json=json_data, timeout=(5, 10))
                    reportcount=reportcount+1
                    print(f"{uid},{response.text},{reportcount}")
                    if reportcount % 30 == 10:
                        with open(log_file, "a", encoding='utf-8') as file:
                            file.write(f"\n{uid},{response.text},{reportcount}")
                except requests.exceptions.RequestException as e:
                    print(e)


            if not offset:
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
