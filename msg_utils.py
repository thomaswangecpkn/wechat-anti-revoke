#!/usr/bin/env python
# -*-encoding:utf-8-*-

import sys, os, time, collections, threading

from html.parser import HTMLParser

from globals import *

nickname = ''

def get_sender_receiver(msg):
    sender = nickname
    receiver = nickname
    if msg['FromUserName'][0:2] == '@@': # group chat
        sender = msg['ActualNickName']
        m = bot.search_chatrooms(userName=msg['FromUserName'])
        if m is not None:
            receiver = m['NickName']
    elif msg['ToUserName'][0:2] == '@@': # group chat by myself
        if 'ActualNickName' in msg:
            sender = msg['ActualNickName']
        else:
            m = bot.search_friends(userName=msg['FromUserName'])
            if m is not None:
                sender = m['NickName']
        m = bot.search_chatrooms(userName=msg['ToUserName'])
        if m is not None:
            receiver = m['NickName']
    else: # personal chat
        m = bot.search_friends(userName=msg['FromUserName'])
        if m is not None:
            sender = m['NickName']
        m = bot.search_friends(userName=msg['ToUserName'])
        if m is not None:
            receiver = m['NickName']
    return HTMLParser().unescape(sender), HTMLParser().unescape(receiver)

def print_msg(msg):
    msg_str = ' '.join(msg)
    print(msg_str)
    return msg_str

def get_whole_msg(msg, download=False):
    sender, receiver = get_sender_receiver(msg)
    if len(msg['FileName']) > 0 and len(msg['Url']) == 0:
        if download: # download the file into data_path directory
            fn = os.path.join(data_path, msg['FileName'])
            msg['Text'](fn)
            if os.path.getsize(fn) == 0:
                return []
            c = '@%s@%s' % (sending_type.get(msg['Type'], 'fil'), fn)
        else:
            c = '@%s@%s' % (sending_type.get(msg['Type'], 'fil'), msg['FileName'])
        return ['[%s]->[%s]:' % (sender, receiver), c]
    c = msg['Text']
    if len(msg['Url']) > 0:
        try: # handle map label
            content_tree = ETree.fromstring(msg['OriContent'])
            if content_tree is not None:
                map_label = content_tree.find('location')
                if map_label is not None:
                    c += ' ' + map_label.attrib['poiname']
                    c += ' ' + map_label.attrib['label']
        except:
            pass
        url = HTMLParser().unescape(msg['Url'])
        c += ' ' + url
    return ['[%s]->[%s]: %s' % (sender, receiver, c)]

def send_msg_to_cbyl(msg_str):
    bot.send(msg_str, toUserName=global_params["cbyl_group_username"])

def send_msg_to_myself(msg_str):
    bot.send(msg_str, toUserName='filehelper')

def broadcast_msg(msg_str):
    if global_params["DEBUG"] == 1:
        send_msg_to_myself(msg_str)
    else:
        send_msg_to_cbyl(msg_str)
