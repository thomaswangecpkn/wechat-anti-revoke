#!/usr/bin/env python
# -*-encoding:utf-8-*-

module_anti_revoke_status = 0

from globals import *

def module_anti_revoke_init():
    module_anti_revoke_status = 1

def anti_revoke_note_msg_process(bot, msg, old_msg):
    msg_send = get_whole_msg(old_msg, download=True)
    for m in msg_send:
        send_msg_to_myself(m)
    if msg['FromUserName'] == global_params["cbyl_group_username"]:
        global_params["cbyl_last_revoke"] = old_msg
    cur_time = time.time()
    if global_params["anti_revoke_status"]["expire_time"] > cur_time:
        for m in msg_send:
            broadcast_msg(m)

def get_dpl_last_revoke():
    pass
    
def get_cbyl_last_revoke():
    pass
    
def open_dpl_revoke_5days():
    pass
    
def open_dpl_revoke_30days():
    pass