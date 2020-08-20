#!/usr/bin/env python
# -*-encoding:utf-8-*-

import collections
import itchat

from db_utils import *

bot = itchat.new_instance()

data_path = 'data'
globals_file_name = "globals.json"
globals_file_path_name = data_path + "/" + globals_file_name

global_params = {
    "DEBUG": 1,
    "VERSION": "V3.0.1",
    "cbyl_group_init_name": "北京的咕咕咕咕菇",
    "cbyl_group_username": None,
    "admin_user_init_name": "逗你玩",
    "admin_user_username": None,
    "keywords_dict": {},
    "ranking_dict": {},
    "anti_revoke_status": { "expire_time": 0 },
    "cbyl_last_revoke": None,
    "dpl_last_revoke": None,
}

def module_globals_init():
    global_params["anti_revoke_status"] = load_json_from_file(globals_file_path_name)

def set_anti_revoke_status(expire_time):
    global_params["anti_revoke_status"]["expire_time"] = expire_time
    save_json_to_file(globals_file_path_name, global_params["anti_revoke_status"])
