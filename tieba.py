# -*- coding:utf-8 -*-
import os
import requests
import hashlib
import time
import copy
import logging
import re


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API_URL
LIKIE_URL = "http://c.tieba.baidu.com/c/f/forum/like"
TBS_URL = "http://tieba.baidu.com/dc/common/tbs"
SIGN_URL = "https://tieba.baidu.com/sign/add"
Ba_TBS = "http://tieba.baidu.com/f?kw="

HEADERS = {
    'Host': 'tieba.baidu.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
    'cookie':'wzws_sessionid=oGQMH7KBMzdmMWJhgmRiMWNhYYAyMDMuMTY4LjUuNzY=; htVC_2132_st_p=0%7C1678504730%7C9215c39a3991781c6bac3bb4a9409325; htVC_2132_visitedfid=8; htVC_2132_viewid=tid_1525747; htVC_2132_saltkey=u8pu8J84; htVC_2132_lastvisit=1678507116; htVC_2132_seccodecS=115885.4b318870f3a008a667; htVC_2132_seccodecSVYY=115884.8bae981cb4692c1aa3; htVC_2132_lastact=1678521003%09member.php%09logging; htVC_2132_ulastactivity=1678521003%7C0; htVC_2132_auth=1b2bF9kqAruJGMTAVan1mbKFyWE5z6UBrM9g%2B%2B3efMfPeddFWMeW8LjU82sOcGjzcewK9oJ89P6P0j%2B%2B%2BbOPIFH6qp2s; htVC_2132_lastcheckfeed=1401788%7C1678521003; htVC_2132_checkfollow=1; htVC_2132_lip=203.168.5.76%2C1678521003', # 此处填写签到时的cookie
}
SIGN_DATA = {
    "ie": "utf-8",
}

SUCCESS_COUNT=0
FAIL_COUNT=0


# VARIABLE NAME
COOKIE = "Cookie"
BDUSS = "bduss"
EQUAL = r'='
EMPTY_STR = r''
TBS = 'tbs'
PAGE_NO = 'page_no'
ONE = '1'
TIMESTAMP = "timestamp"
DATA = 'data'
FID = 'fid'
SIGN_KEY = 'tiebaclient!!!'
UTF8 = "utf-8"
SIGN = "sign"
KW = "kw"

s = requests.Session()


def get_tbs(bduss):
    logger.info("获取tbs开始")
    headers = copy.copy(HEADERS)
    headers.update({COOKIE: EMPTY_STR.join([BDUSS, EQUAL, bduss])})
    try:
        tbs = s.get(url=TBS_URL, headers=headers, timeout=5).json()[TBS]
    except Exception as e:
        logger.error("获取tbs出错" + e)
        logger.info("重新获取tbs开始")
        tbs = s.get(url=TBS_URL, headers=headers, timeout=5).json()[TBS]
    logger.info("获取tbs结束")
    return tbs


def get_favorite(bduss):
    logger.info("获取关注的贴吧开始")
    # 客户端关注的贴吧
    returnData = {}
    i = 1
    data = {
        'BDUSS': bduss,
        '_client_type': '2',
        '_client_id': 'wappc_1534235498291_488',
        '_client_version': '9.7.8.0',
        '_phone_imei': '000000000000000',
        'from': '1008621y',
        'page_no': '1',
        'page_size': '200',
        'model': 'MI+5',
        'net_type': '1',
        'timestamp': str(int(time.time())),
        'vcode_tag': '11',
    }
    data = encodeData(data)
    try:
        res = s.post(url=LIKIE_URL, data=data, timeout=5).json()
    except Exception as e:
        logger.error("获取关注的贴吧出错" + e)
        return []
    returnData = res
    if 'forum_list' not in returnData:
        returnData['forum_list'] = []
    if res['forum_list'] == []:
        return {'gconforum': [], 'non-gconforum': []}
    if 'non-gconforum' not in returnData['forum_list']:
        returnData['forum_list']['non-gconforum'] = []
    if 'gconforum' not in returnData['forum_list']:
        returnData['forum_list']['gconforum'] = []
    while 'has_more' in res and res['has_more'] == '1':
        i = i + 1
        data = {
            'BDUSS': bduss,
            '_client_type': '2',
            '_client_id': 'wappc_1534235498291_488',
            '_client_version': '9.7.8.0',
            '_phone_imei': '000000000000000',
            'from': '1008621y',
            'page_no': str(i),
            'page_size': '200',
            'model': 'MI+5',
            'net_type': '1',
            'timestamp': str(int(time.time())),
            'vcode_tag': '11',
        }
        data = encodeData(data)
        try:
            res = s.post(url=LIKIE_URL, data=data, timeout=5).json()
        except Exception as e:
            logger.error("获取关注的贴吧出错" + e)
            continue
        if 'forum_list' not in res:
            continue
        if 'non-gconforum' in res['forum_list']:
            returnData['forum_list']['non-gconforum'].append(res['forum_list']['non-gconforum'])
        if 'gconforum' in res['forum_list']:
            returnData['forum_list']['gconforum'].append(res['forum_list']['gconforum'])

    t = []
    for i in returnData['forum_list']['non-gconforum']:
        if isinstance(i, list):
            for j in i:
                if isinstance(j, list):
                    for k in j:
                        t.append(k)
                else:
                    t.append(j)
        else:
            t.append(i)
    for i in returnData['forum_list']['gconforum']:
        if isinstance(i, list):
            for j in i:
                if isinstance(j, list):
                    for k in j:
                        t.append(k)
                else:
                    t.append(j)
        else:
            t.append(i)
    logger.info("获取关注的贴吧结束")
    return t


def encodeData(data):
    s = EMPTY_STR
    keys = data.keys()
    for i in sorted(keys):
        s += i + EQUAL + str(data[i])
    sign = hashlib.md5((s + SIGN_KEY).encode(UTF8)).hexdigest().upper()
    data.update({SIGN: str(sign)})
    return data

def getTbs(kw):
    # 正则表达式学得不太好，用得有点呆板，凑合用
    url = "https://tieba.baidu.com/f?kw="+kw+"&fr=index&fp=0&ie=utf-8"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    response.encoding = response.apparent_encoding
    html = response.text
    match = re.search(r"'tbs': \"(.*)\"    };", html)
    if match:
        tbs = match.group(0).split('"')[1]
        return tbs
    return None


def client_sign(bduss, tbs, fid, kw):
    global SUCCESS_COUNT
    global FAIL_COUNT
    # 客户端签到
    logger.info("开始签到贴吧：" + kw)
    data = copy.copy(SIGN_DATA)
    tbs = getTbs(kw)
    data.update({BDUSS: bduss, FID: fid, KW: kw, TBS: tbs, TIMESTAMP: str(int(time.time()))})
    data = encodeData(data)
    res = s.post(url=SIGN_URL,headers=HEADERS, data=data, timeout=5).json()
    if res.get("no") == 0:
        SUCCESS_COUNT += 1
        print("成功")
    else:
        FAIL_COUNT += 1
        print("失败")
        


def main():
    global SUCCESS_COUNT
    global FAIL_COUNT
    b = "BDUSS" # 此处填写bduss
    print("开始签到")
    tbs = get_tbs(b)
    favorites = get_favorite(b)
    for j in favorites:
        client_sign(b, tbs, j["id"], j["name"])
    print("本次签到成功%d个，失败%d个" % (SUCCESS_COUNT, FAIL_COUNT))
    # 此处****替换为server酱个人key
    text = 'https://sctapi.ftqq.com/*************.send?title=贴吧签到成功'+str(SUCCESS_COUNT)+'个，失败'+ str(FAIL_COUNT)+"个"+' &desp=签到成功！！'
    requests.get(text)



if __name__ == '__main__':
    main()
