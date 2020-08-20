#!/usr/bin/env python
# -*-encoding:utf-8-*-

from datetime import date, timedelta
import time

from globals import *
from db_utils import *
from msg_utils import *

data_path = 'data'
keyword_award_file_name = "keyword_award.json"
ranking_file_name = "ranking.json"
keyword_award_file_path_name = data_path + "/" + keyword_award_file_name
ranking_file_path_name = data_path + "/" + ranking_file_name
module_keyword_award_status = 0
default_expire_time = 3600 * 2

def module_keyword_award_init():
    global_params["keywords_dict"] = load_json_from_file(keyword_award_file_path_name)
    global_params["ranking_dict"] = load_json_from_file(ranking_file_path_name)
    module_keyword_award_status = 1

def get_next_day_time(cur_time):
    y = int((date.today() + timedelta(days= 1)).strftime("%Y"))
    m = int((date.today() + timedelta(days= 1)).strftime("%m"))
    d = int((date.today() + timedelta(days= 1)).strftime("%d"))
    return time.mktime((y, m, d, 0, 0, 0, 0, 0, 0))

def get_next_valid_time(key):
    cur_time = time.time()
    next_time = cur_time + default_expire_time
    if key not in global_params["keywords_dict"]["data"].keys():
        print("get_next_valid_time failed! key(%s) not in keywords_dict" % key)
        return next_time
    if "type" not in global_params["keywords_dict"]["data"][key].keys():
        print("get_next_valid_time failed! \"type\" not in keywords_dict[%s]" % key)
        return next_time
    if "expire_time" not in global_params["keywords_dict"]["data"][key].keys():
        print("get_next_valid_time failed! \"expire_time\" not in keywords_dict[%s]" % key)
        return next_time
    
    if global_params["keywords_dict"]["data"][key]["type"] == "expire":
        return cur_time + global_params["keywords_dict"]["data"][key]["expire_time"]
    elif global_params["keywords_dict"]["data"][key]["type"] == "schedule":
        return get_next_day_time(cur_time)
    else:
        print("get_next_valid_time failed! inavlid key(%s) type(%s)" % (key, global_params["keywords_dict"]["data"][key]["type"]))
        return next_time

def search_keyword_in_msg(msg_str):
    for key in global_params["keywords_dict"]["data"].keys():
        if key in msg_str:
            cur_time = time.time()
            if global_params["keywords_dict"]["data"][key]["next_valid_time"] <= cur_time:
                return key
    return None

def get_award_msg(sender, key):
    if key not in global_params["keywords_dict"]["data"].keys():
        return None
    if sender not in global_params["ranking_dict"].keys():
        return None
    send_msg = "[" + sender + "]在群聊中击中了关键字[" + key + "], 获得" + str(global_params["keywords_dict"]["data"][key]["award_score"]) + "积分, 当前积分:" + str(global_params["ranking_dict"][sender])
    return send_msg

def add_score(sender, key):
    if key not in global_params["keywords_dict"]["data"].keys():
        return None
    if sender in global_params["ranking_dict"].keys():
        global_params["ranking_dict"][sender] += global_params["keywords_dict"]["data"][key]["award_score"]
    else:
        global_params["ranking_dict"][sender] = global_params["keywords_dict"]["data"][key]["award_score"]
    global_params["keywords_dict"]["data"][key]["next_valid_time"] = get_next_valid_time(key)
    save_json_to_file(keyword_award_file_path_name, global_params["keywords_dict"])
    save_json_to_file(ranking_file_path_name, global_params["ranking_dict"])
    return None

def keyword_award_normal_msg_process(msg):
    if global_params["DEBUG"] == 0 and msg['FromUserName'] != global_params["cbyl_group_username"]:
        return False
    if global_params["DEBUG"] == 1 and msg['FromUserName'] != global_params["cbyl_group_username"] and (msg['FromUserName'] != global_params["admin_user_username"] or msg['ToUserName'] != global_params["admin_user_username"]):
        return False
    if len(msg['FileName']) > 0 and len(msg['Url']) == 0:
        return False
    msg_str = msg['Text']
    key = search_keyword_in_msg(msg_str)
    if key:
        sender, receiver = get_sender_receiver(msg)
        add_score(sender, key)
        broadcast_msg(get_award_msg(sender, key))
        return True
    return False

def get_score(sender):
    if sender not in global_params["ranking_dict"].keys():
        global_params["ranking_dict"][sender] = 0
    return global_params["ranking_dict"][sender]

def pay_score(sender, pay_score):
    user_score = get_score(sender)
    if user_score < pay_score:
        return False
    global_params["ranking_dict"][sender] -= pay_score
    save_json_to_file(ranking_file_path_name, global_params["ranking_dict"])
    return True

def add_keyword(key, score=10, expire_time=3600):
    global_params["keywords_dict"]["data"][key] = dict()
    global_params["keywords_dict"]["data"][key]["award_score"] = score
    global_params["keywords_dict"]["data"][key]["expire_time"] = expire_time
    global_params["keywords_dict"]["data"][key]["type"] = "expire"
    global_params["keywords_dict"]["data"][key]["next_valid_time"] = 0
    save_json_to_file(keyword_award_file_path_name, global_params["keywords_dict"])


    