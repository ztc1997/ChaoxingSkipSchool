import hashlib
import time

import pyDes

__doc__ = '处理超星相关的加密和效验码计算'

KEY_DES_URL = "Z(AfY@XS"
KEY_DES_USER_PWD = "L(AfY@DE"


def md5_string(plain):
    m = hashlib.md5()
    m.update(plain.encode("utf-8"))
    return m.hexdigest()


def des_string(key, plain):
    return bytes_to_hex_string(des_bytes(key, plain))


def des_bytes(key, plain):
    enc_bytes = pyDes.des(key).encrypt(plain, padmode=pyDes.PAD_PKCS5)
    return enc_bytes


def bytes_to_hex_string(src):
    ret = ""
    for b in src:
        ret += "%X" % b
    return ret


# 生成获取课程列表的url，带有时间戳
def chaoxing_get_subscribe_url():
    url_base = "http://apps.chaoxing.com/apis/subscribe/getSubscribe.jspx?"
    time_ms = round(time.time() * 1000)
    url_params = "token=4faa8662c59590c6f43ae9fe5b002b42&_time=%s&cataid=-1&refresh=1&splitData=1&version=8.0" % time_ms
    url = url_base + url_params + "&inf_enc=" + md5_string(url_params + "&DESKey=" + KEY_DES_URL)
    return url


# 根据超星标准加密密码
def chaoxing_user_pwd_enc(pwd):
    return des_string(KEY_DES_USER_PWD, pwd)


# 计算视频播放时间报告的效验码
def chaoxin_video_report_url_enc(clazz_id, user_id, job_id, object_id, playing_time, duration):
    plain = '[%s][%s][%s][%s][%s][d_yHJ!$pdA~5][%s][0_%s]' % (
        clazz_id, user_id, job_id, object_id, playing_time * 1000, duration * 1000, duration)
    return md5_string(plain)


# 生成视频播放时间报告的url
def chaoxin_video_report_url(dtoken, other_info, playing_time, duration, job_id, clazz_id, object_id, user_id, is_drag):
    url = ('http://mooc1-api.chaoxing.com/multimedia/log/%s?otherInfo=%s&playingTime=%d&duration=%d&akid=null'
           '&jobid=%s&clipTime=%s&clazzId=%s&objectId=%s&userid=%s&isdrag=%d&enc=%s&dtype=Video&view=json') % (
              dtoken, other_info, playing_time, duration, job_id, '0_' + str(duration), clazz_id, object_id, user_id,
              is_drag, chaoxin_video_report_url_enc(clazz_id, user_id, job_id, object_id, playing_time, duration)
          )
    return url
