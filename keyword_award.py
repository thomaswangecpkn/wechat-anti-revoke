#!/usr/bin/env python
# -*-encoding:utf-8-*-

import time, random
from datetime import date, timedelta

from globals import *
from db_utils import *
from msg_utils import *

keyword_award_file_name = "keyword_award.json"
ranking_file_name = "ranking.json"
keyword_list_init_file_name = "keyword_list_init.json"
keyword_award_file_path_name = global_params["data_path"] + "/" + keyword_award_file_name
ranking_file_path_name = global_params["data_path"] + "/" + ranking_file_name
keyword_list_init_file_path_name = global_params["src_data_path"] + "/" + keyword_list_init_file_name

default_expire_time = 60 * 60 * 24 * 30
max_award_in_10min = 3

def load_init_keyword():
    keyword_init_dict = load_json_from_file(keyword_list_init_file_path_name)
    if type(keyword_init_dict) is not dict:
        dbg_log("load_init_keyword failed.")
        return
    load_count_total = 0
    for data_set in keyword_init_dict["data_sets"]:
        expire_type = keyword_init_dict["data_types"][data_set["data_type"]]["expire_type"]
        expire_time = keyword_init_dict["data_types"][data_set["data_type"]]["expire_time"]
        award_type = keyword_init_dict["data_types"][data_set["data_type"]]["award_type"]
        if award_type == "fix":
            award_score = keyword_init_dict["data_types"][data_set["data_type"]]["award_score"]
        elif award_type == "aug":
            start_score = keyword_init_dict["data_types"][data_set["data_type"]]["start_score"]
            step_score = keyword_init_dict["data_types"][data_set["data_type"]]["step_score"]
        else:
            continue
        load_count_local = 0
        for kw in data_set["key_words"]:
            if kw not in global_params["keywords_dict"].keys():
                global_params["keywords_dict"][kw] = dict()
                global_params["keywords_dict"][kw]["next_valid_time"] = 0
            global_params["keywords_dict"][kw]["type"] = expire_type
            global_params["keywords_dict"][kw]["expire_time"] = expire_time
            if award_type == "fix":
                global_params["keywords_dict"][kw]["award_score"] = award_score
            if award_type == "aug":
                global_params["keywords_dict"][kw]["award_score"] = start_score + load_count_local * step_score
            load_count_local += 1
        dbg_log("Load keyword in dataset(%s): %d" % (data_set["data_type"], load_count_local))
        load_count_total += load_count_local
    dbg_log("Total load init keyword: %d" % load_count_total)
    save_json_to_file(keyword_award_file_path_name, global_params["keywords_dict"])
    return

def module_keyword_award_init():
    global keyword_award_file_path_name, ranking_file_path_name, keyword_list_init_file_path_name
    keyword_award_file_path_name = global_params["data_path"] + "/" + keyword_award_file_name
    ranking_file_path_name = global_params["data_path"] + "/" + ranking_file_name
    keyword_list_init_file_path_name = global_params["src_data_path"] + "/" + keyword_list_init_file_name
    
    global_params["keywords_dict"] = load_json_from_file(keyword_award_file_path_name)
    if type(global_params["keywords_dict"]) is not dict:
        global_params["keywords_dict"] = {}
    global_params["ranking_dict"] = load_json_from_file(ranking_file_path_name)
    if type(global_params["ranking_dict"]) is not dict:
        global_params["ranking_dict"] = {}
        
    load_init_keyword()

def get_next_day_time():
    y = int((date.today() + timedelta(days=1)).strftime("%Y"))
    m = int((date.today() + timedelta(days=1)).strftime("%m"))
    d = int((date.today() + timedelta(days=1)).strftime("%d"))
    return time.mktime((y, m, d, 0, 0, 0, 0, 0, 0))

def get_random_coeff():
    return random.uniform(0.5, 1.5)

def get_next_valid_time(key):
    cur_time = time.time()
    next_time = cur_time + default_expire_time * get_random_coeff()
    if key not in global_params["keywords_dict"].keys():
        dbg_log("get_next_valid_time failed! key(%s) not in keywords_dict" % key)
        return next_time
    if "type" not in global_params["keywords_dict"][key].keys():
        dbg_log("get_next_valid_time failed! \"type\" not in keywords_dict[%s]" % key)
        return next_time
    if "expire_time" not in global_params["keywords_dict"][key].keys():
        dbg_log("get_next_valid_time failed! \"expire_time\" not in keywords_dict[%s]" % key)
        return next_time
    
    if global_params["keywords_dict"][key]["type"] == "expire":
        return cur_time + global_params["keywords_dict"][key]["expire_time"] * get_random_coeff()
    elif global_params["keywords_dict"][key]["type"] == "schedule":
        return get_next_day_time()
    else:
        dbg_log("get_next_valid_time failed! inavlid key(%s) type(%s)" % (key, global_params["keywords_dict"][key]["type"]))
        return next_time  

def get_punish_msg(sender, score_taken):
    if sender not in global_params["ranking_dict"].keys():
        return None
    send_msg = "[" + sender + "]在群聊中击中了防刷屏保护, 扣除" + str(score_taken) + "积分, 当前积分:" +  str(global_params["ranking_dict"][sender]["score"])
    return send_msg

def search_keyword_in_msg(msg_str):
    for key in global_params["keywords_dict"].keys():
        if key in msg_str:
            cur_time = time.time()
            if global_params["keywords_dict"][key]["next_valid_time"] <= cur_time:
                return key
    return None

def check_if_abuse(msg_str):
    match_count = 0
    for key in global_params["keywords_dict"].keys():
        if key in msg_str:
            match_count += 1
    if match_count >= 3:
        return match_count
    return 0
    
def get_award_msg(sender, key):
    if key not in global_params["keywords_dict"].keys():
        return None
    if sender not in global_params["ranking_dict"].keys():
        return None
    send_msg = "[" + sender + "]在群聊中击中了关键字[" + key + "], 获得" + str(global_params["keywords_dict"][key]["award_score"]) + "积分, 当前积分:" + str(global_params["ranking_dict"][sender]["score"])
    return send_msg    
    
def add_score_by_key(sender, key):
    if key not in global_params["keywords_dict"].keys():
        return None
    if sender not in global_params["ranking_dict"].keys():
        global_params["ranking_dict"][sender] = {}
    if "score" not in global_params["ranking_dict"][sender].keys():
        global_params["ranking_dict"][sender]["score"] = 0
    global_params["ranking_dict"][sender]["score"] = global_params["keywords_dict"][key]["award_score"]
    global_params["keywords_dict"][key]["next_valid_time"] = get_next_valid_time(key)
    add_hit_time(sender)
    save_json_to_file(keyword_award_file_path_name, global_params["keywords_dict"])
    save_json_to_file(ranking_file_path_name, global_params["ranking_dict"])
    return None

def add_score_direct(sender, score):
    if sender not in global_params["ranking_dict"].keys():
        global_params["ranking_dict"][sender] = {}
    if "score" not in global_params["ranking_dict"][sender].keys():
        global_params["ranking_dict"][sender]["score"] = 0
    global_params["ranking_dict"][sender]["score"] += score
    save_json_to_file(ranking_file_path_name, global_params["ranking_dict"])
    return

def take_score(sender, score_taken):
    if sender not in global_params["ranking_dict"].keys():
        global_params["ranking_dict"][sender] = {}
    if "score" not in global_params["ranking_dict"][sender].keys():
        global_params["ranking_dict"][sender]["score"] = 0
    global_params["ranking_dict"][sender]["score"] -= score_taken
    save_json_to_file(ranking_file_path_name, global_params["ranking_dict"])
    return

def check_hit_time(sender):
    if sender not in global_params["ranking_dict"].keys():
        global_params["ranking_dict"][sender] = {}
    if "hit_time_list" not in global_params["ranking_dict"][sender].keys():
        global_params["ranking_dict"][sender]["hit_time_list"] = []
        return True
    if len(global_params["ranking_dict"][sender]["hit_time_list"]) >= max_award_in_10min:
        cur_time = time.time()
        if global_params["ranking_dict"][sender]["hit_time_list"][0] > cur_time - 10 * 60:
            dbg_log("%s is in cd(%f), cannot add score" % (sender, cur_time - global_params["ranking_dict"][sender]["hit_time_list"][0]))
            return False
    return True

def add_hit_time(sender):
    if sender not in global_params["ranking_dict"].keys():
        global_params["ranking_dict"][sender] = {}
    if "hit_time_list" not in global_params["ranking_dict"][sender].keys():
        global_params["ranking_dict"][sender]["hit_time_list"] = []
    cur_time = time.time()
    list_len = len(global_params["ranking_dict"][sender]["hit_time_list"])
    if list_len >= max_award_in_10min:
        global_params["ranking_dict"][sender]["hit_time_list"].pop(0)
    global_params["ranking_dict"][sender]["hit_time_list"].append(cur_time)
    return

def keyword_award_normal_msg_process(msg):
    if global_params["DEBUG"] == 0 and msg['FromUserName'] != global_params["cbyl_group_username"]:
        return False
    if global_params["DEBUG"] == 1 and msg['FromUserName'] != global_params["cbyl_group_username"] and (msg['FromUserName'] != global_params["admin_user_username"] or msg['ToUserName'] != global_params["admin_user_username"]):
        return False
    if len(msg['FileName']) > 0 and len(msg['Url']) == 0:
        return False
    msg_str = msg['Text']
    abuse_punish = check_if_abuse(msg_str)
    if abuse_punish > 0:
        sender, receiver = get_sender_receiver(msg)
        take_score(sender, abuse_punish)
        broadcast_msg(get_punish_msg(sender, abuse_punish))
        return True
    key = search_keyword_in_msg(msg_str)
    if key:
        sender, receiver = get_sender_receiver(msg)
        if check_hit_time(sender):
            add_score_by_key(sender, key)
            broadcast_msg(get_award_msg(sender, key))
            return True
    return False

def get_score(sender):
    if sender not in global_params["ranking_dict"].keys():
        global_params["ranking_dict"][sender] = {}
    if "score" not in global_params["ranking_dict"][sender].keys():
        global_params["ranking_dict"][sender]["score"] = 0
    return global_params["ranking_dict"][sender]["score"]

def pay_score(sender, pay_score):
    user_score = get_score(sender)
    if user_score < pay_score:
        return False
    global_params["ranking_dict"][sender]["score"] -= pay_score
    save_json_to_file(ranking_file_path_name, global_params["ranking_dict"])
    return True
 
def add_keyword(key, score=10, expire_time=3600):
    global_params["keywords_dict"][key] = dict()
    global_params["keywords_dict"][key]["award_score"] = score
    global_params["keywords_dict"][key]["expire_time"] = expire_time
    global_params["keywords_dict"][key]["type"] = "expire"
    global_params["keywords_dict"][key]["next_valid_time"] = 0
    save_json_to_file(keyword_award_file_path_name, global_params["keywords_dict"])

    