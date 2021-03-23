#!/usr/bin/env python
# -*-encoding:utf-8-*-

import os, collections, platform
import itchat

from db_utils import *

bot = itchat.new_instance()

global_params = {
    "DEBUG": 1,
    "data_path": "/home/data",
    "src_data_path": "data",
    "VERSION": "V3.1.1",
    "cbyl_group_init_name": "咕咕咕咕咕咕咕咕咕咕咕咕咕咕咕呱",
    "cbyl_group_username": None,
    "admin_user_init_name": "逗你玩",
    "admin_user_username": None,
    "keywords_dict": None,
    "ranking_dict": None,
    "anti_revoke_status": None,
    "cbyl_last_revoke": None,
    "dpl_last_revoke": None,
    "word_statis": None,
    "speak_statis": None,
}

globals_file_name = "globals.json"
globals_file_path_name = global_params["data_path"] + "/" + globals_file_name

def get_data_path():
    if platform.system() == 'Linux':
        return "/home/data"
    return "data"

def module_globals_init():
    global_params["data_path"] = get_data_path()
    if not os.path.exists(global_params["data_path"]):
        os.mkdir(global_params["data_path"])
    global_params["anti_revoke_status"] = load_json_from_file(globals_file_path_name)
    if type(global_params["anti_revoke_status"]) is not dict or "expire_time" not in global_params["anti_revoke_status"].keys():
        global_params["anti_revoke_status"] = { "expire_time": 0 }
    if type(global_params["word_statis"]) is not dict:
        global_params["word_statis"] = dict()
    if type(global_params["speak_statis"]) is not dict:
        global_params["speak_statis"] = dict()

def set_anti_revoke_status(expire_time):
    global_params["anti_revoke_status"]["expire_time"] = expire_time
    save_json_to_file(globals_file_path_name, global_params["anti_revoke_status"])

def dbg_log(str):
    if global_params["DEBUG"]:
        print(str)

def msg_print(str):
    try:
        print(str)
    except Exception as e:
        dbg_log(e)