#!/usr/bin/env python
# -*-encoding:utf-8-*-

import sys, os, time, collections, threading, platform

from html.parser import HTMLParser
from xml.etree import ElementTree as ETree

import itchat
from itchat.content import *

from globals import *
from msg_utils import *
from anti_revoke import anti_revoke_note_msg_process
from keyword_award import keyword_award_normal_msg_process
from command_helper import command_helper_normal_msg_process

msg_store = collections.OrderedDict()
timeout = 600
sending_type = {'Picture': 'img', 'Video': 'vid'}
data_path = 'data'

def get_qr_type():
    if platform.system() == 'Linux':
        return 2
    return 1

def module_msg_box_init():
    if not os.path.exists(data_path):
        os.mkdir(data_path)
    # if the QR code doesn't show correctly, you can try to change the value
    # of enableCdmQR to 1 or -1 or -2. It nothing works, you can change it to
    # enableCmdQR=True and a picture will show up.
    bot.auto_login(hotReload=False, enableCmdQR=get_qr_type())
    nickname = bot.loginInfo['User']['NickName']
    while 1:
        cbyl_group_instance = bot.search_chatrooms(name=global_params["cbyl_group_init_name"])
        if type(cbyl_group_instance) is list and len(cbyl_group_instance) == 1:
            global_params["cbyl_group_username"] = cbyl_group_instance[0]["UserName"]
            break
        global_params["cbyl_group_init_name"] = input("cbyl group name:")
    while 1:
        admin_user_instance = bot.search_friends(name=global_params["admin_user_init_name"])
        if type(admin_user_instance) is list and len(admin_user_instance) == 1:
            global_params["admin_user_username"] = admin_user_instance[0]["UserName"]
            break
        global_params["admin_user_init_name"] = input("admin name:")

def time_thread_keeping_login():
    bot.get_contact()
    t = threading.Timer(300, time_thread_keeping_login)
    t.start()
        
def module_msg_box_run():
    time_thread_keeping_login()
    bot.run()

def normal_msg_process(bot, msg):
    if (msg['FromUserName'] == global_params["admin_user_username"] and msg['ToUserName'] == global_params["admin_user_username"]) or \
       (msg['FromUserName'] == global_params["cbyl_group_username"] and msg['ActualNickName'] != global_params["admin_user_init_name"]):
        if command_helper_normal_msg_process(msg):
            return True
        if keyword_award_normal_msg_process(msg):
            return True
    return False

def note_msg_process(bot, msg, old_msg):
    anti_revoke_note_msg_process(bot, msg, old_msg)

@bot.msg_register([TEXT, PICTURE, MAP, CARD, SHARING, RECORDING,
    ATTACHMENT, VIDEO, FRIENDS], isFriendChat=True, isGroupChat=True)
def normal_msg(msg):
    print_msg(get_whole_msg(msg))
    now = time.time()
    msg['ReceivedTime'] = now
    msg_id = msg['MsgId']
    msg_store[msg_id] = msg
    normal_msg_process(bot, msg)
    clear_timeouted_message()

@bot.msg_register([NOTE], isFriendChat=True, isGroupChat=True)
def note_msg(msg):
    sender, receiver = get_sender_receiver(msg)
    print_msg(get_whole_msg(msg))
    content = HTMLParser().unescape(msg['Content'])
    try:
        content_tree = ETree.fromstring(content)
    except Exception:
        # invent/remove to chatroom
        return
    if content_tree is None:
        return
    revoked = content_tree.find('revokemsg')
    if revoked is None:
        return
    old_msg_id = revoked.find('msgid').text
    old_msg = msg_store.get(old_msg_id)
    if old_msg is None:
        return
    msg_send = get_whole_msg(old_msg, download=True)
    note_msg_process(bot, msg, old_msg)
    clear_timeouted_message()

def clear_timeouted_message():
    now = time.time()
    count = 0
    for k, v in msg_store.items():
        if now - v['ReceivedTime'] > timeout:
            count += 1
        else:
            break
    for i in range(count):
        item = msg_store.popitem(last=False)
