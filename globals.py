#!/usr/bin/env python
# -*-encoding:utf-8-*-

import collections

import itchat

bot = itchat.new_instance()

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


