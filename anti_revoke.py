#!/usr/bin/env python
# -*-encoding:utf-8-*-

import time

from globals import *
from msg_utils import *

module_anti_revoke_status = 0

def module_anti_revoke_init():
    module_anti_revoke_status = 1

def anti_revoke_note_msg_process(bot, msg, old_msg):
    msg_send = get_whole_msg(old_msg, download=True)
    for m in msg_send:
        send_msg_to_myself(m, toUserName='filehelper')
    for m in msg_send:
        send_msg_to_myself(m)
    if msg['FromUserName'] == global_params["cbyl_group_username"]:
        global_params["cbyl_last_revoke"] = old_msg
        if msg['ActualNickName'] == "hugo": #TODO!!
            global_params["dpl_last_revoke"] = old_msg
    cur_time = time.time()
    if global_params["anti_revoke_status"]["expire_time"] > cur_time:
        for m in msg_send:
            broadcast_msg(m)

def get_dpl_last_revoke(msg):
    msg_send = get_whole_msg(global_params["dpl_last_revoke"], download=True)
    for m in msg_send:
        broadcast_msg(m)
    return
    
def get_cbyl_last_revoke(msg):
    msg_send = get_whole_msg(global_params["cbyl_last_revoke"], download=True)
    for m in msg_send:
        broadcast_msg(m)
    return
    
def open_dpl_revoke_5days(msg):
    cur_time = time.time()
    add_time = 5 * 24 * 60 * 60
    set_anti_revoke_status(max(global_params["anti_revoke_status"]["expire_time"], cur_time) + add_time)
    msg_send = "防饺子撤回神器已开启, 有效期至" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(global_params["anti_revoke_status"]["expire_time"]))
    broadcast_msg(msg_send)
    return
    
def open_dpl_revoke_30days(msg):
    cur_time = time.time()
    add_time = 30 * 24 * 60 * 60
    set_anti_revoke_status(max(global_params["anti_revoke_status"]["expire_time"], cur_time) + add_time)
    msg_send = "防饺子撤回神器已开启, 有效期至" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(global_params["anti_revoke_status"]["expire_time"]))
    broadcast_msg(msg_send)
    return
