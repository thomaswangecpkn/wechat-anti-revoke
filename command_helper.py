#!/usr/bin/env python
# -*-encoding:utf-8-*-

from globals import *
from msg_utils import *
from anti_revoke import get_dpl_last_revoke, get_cbyl_last_revoke, open_dpl_revoke_5days, open_dpl_revoke_30days
from keyword_award import get_score, pay_score, add_keyword, add_score_direct, default_expire_time

DEFAULT_SCORE = 10

def user_get_helper(msg):
    send_msg = "防饺子撤回神器" + global_params["VERSION"] + ", 使用方法\n" \
             + "\"#帮助\": 查询本帮助\n" \
             + "\"#查询\": 查询积分\n" \
             + "\"#兑换 + 数字(如:兑换1)\": 兑换功能, 目前支持的功能有:\n" \
             + "    1. 查看饺子上一条撤回的消息[200积分]\n" \
             + "    2. 查看群聊上一条撤回的消息[200积分]\n" \
             + "    3. 打开防饺子撤回神器[500积分, 有效期5天]\n" \
             + "    4. 打开防饺子撤回神器[1000积分, 有效期30天]\n" \
             + "【更多功能敬请期待!】"
    broadcast_msg(send_msg)
    return

def user_get_score(msg):
    sender, receiver = get_sender_receiver(msg)
    score = get_score(sender)
    send_msg = "[" + sender + "]当前积分:" + str(score)
    broadcast_msg(send_msg)
    return

def user_get_statis(msg):
    lst = sorted(global_params["word_statis"].items(), key=lambda d: d[1], reverse=True)
    send_msg = "防饺子撤回神器" + global_params["VERSION"] + ", 大划子统计\n"
    if len(lst) >= 1:
        send_msg += lst[0][0] + ": " + "划水" + str(global_params["speak_statis"][lst[0][0]]) + "次, 共计" + str(global_params["word_statis"][lst[0][0]]) + "词, 获得称号【老划子】\n"
    if len(lst) >= 2:
        send_msg += lst[1][0] + ": " + "划水" + str(global_params["speak_statis"][lst[1][0]]) + "次, 共计" + str(global_params["word_statis"][lst[1][0]]) + "词, 获得称号【大划子】\n"
    if len(lst) >= 3:
        send_msg += lst[2][0] + ": " + "划水" + str(global_params["speak_statis"][lst[2][0]]) + "次, 共计" + str(global_params["word_statis"][lst[2][0]]) + "词, 获得称号【小划子】"
    broadcast_msg(send_msg)
    return
    
bonus_dict = {
    1: { "cost": 200, "func": get_dpl_last_revoke },
    2: { "cost": 200, "func": get_cbyl_last_revoke },
    3: { "cost": 500, "func": open_dpl_revoke_5days },
    4: { "cost": 1000, "func": open_dpl_revoke_30days },
}

def user_get_bonus(msg):
    msg_str = msg['Text']
    i = msg_str.find("#兑换")
    if i < 0 or len(msg_str) <= i + 3:
        return
    if not msg_str[i + 3].isdigit():
        return
    bonusIdx = int(msg_str[i + 3])
    if bonusIdx not in bonus_dict.keys():
        return
    sender, receiver = get_sender_receiver(msg)
    score = get_score(sender)
    if not pay_score(sender, bonus_dict[bonusIdx]["cost"]):
        send_msg = "积分不足! 功能[" + str(bonusIdx) + "]需要" + str(bonus_dict[bonusIdx]["cost"]) + "分, [" + sender + "]当前积分:" + str(score)
    else:
        bonus_dict[bonusIdx]["func"](msg)
        send_msg = "[" + sender + "]兑换功能[" + str(bonusIdx) + "]成功! 当前积分:" + str(score)
    broadcast_msg(send_msg)
    return

def admin_change_debug_mode(msg):
    msg_str = msg['Text']
    msgs = msg_str.split(' ')
    if msgs[0] != "##DEBUG":
        dbg_log("admin_change_debug_mode failed! msgs[0](%s)" % msgs[0])
        return
    if not msgs[1].isnumeric():
        dbg_log("admin_change_debug_mode failed! msgs[1](%s)" % msgs[1])
        return
    orig_debug = global_params["DEBUG"]
    new_debug = int(msgs[1])
    if new_debug != 0 and new_debug != 1:
        dbg_log("admin_change_debug_mode failed! new_debug(%d)" % new_debug)
        return
    global_params["DEBUG"] = new_debug
    send_msg_to_myself("更改DEBUG模式[" + str(orig_debug) + "]->[" + str(new_debug) + "]")
    return
    
def admin_add_key_word(msg):
    # ##ADDKEY KEYWORD SCORE EXPIRE_TIME
    msg_str = msg['Text']
    msgs = msg_str.split(' ')
    keyword = ""
    score = DEFAULT_SCORE
    expire_time = default_expire_time
    
    if msgs[0] != "##AK":
        dbg_log("admin_add_key_word failed! msgs[0](%s)" % msgs[0])
        return
    if len(msgs) < 1:
        dbg_log("admin_add_key_word failed! msglen(%d)" % len(msgs))
        return
    if len(msgs) > 1:
        keyword = msgs[1]
    if len(msgs) > 2:
        score = int(msgs[2])
    if len(msgs) > 3:
        expire_time = int(msgs[3])
    add_keyword(keyword, score, expire_time)
    send_msg_to_myself("增加关键词" + keyword + " " + str(score) + " " + str(expire_time))
    return

def admin_add_score(msg):
    # ##AS NICKNAME SCORE
    msg_str = msg['Text']
    msgs = msg_str.split(' ')
    if msgs[0] != "##AS":
        dbg_log("admin_add_score failed! msgs[0](%s)" % msgs[0])
        return
    if len(msgs) != 3:
        dbg_log("admin_add_score failed! msglen(%d)" % len(msgs))
        return
    sender = msgs[1]
    score = int(msgs[2])
    cur_score = add_score_direct(sender, score)
    send_msg_to_myself("为" + sender + "增加" + str(score) + "分, 当前积分: " + str(cur_score))
    return

command_dict = {
    "#帮助" : user_get_helper,
    "#查询" : user_get_score,
    "#兑换" : user_get_bonus,
    "#统计" : user_get_statis
}

admin_command_dict = {
    "##DEBUG" : admin_change_debug_mode,
    "##AK" : admin_add_key_word,
    "##AS" : admin_add_score
}

def command_helper_normal_msg_process(msg):
    if msg['FromUserName'] != global_params["cbyl_group_username"] and (msg['FromUserName'] != global_params["admin_user_username"] or msg['ToUserName'] != global_params["admin_user_username"]):
        return False
    if len(msg['FileName']) > 0 and len(msg['Url']) == 0:
        return False
    msg_str = msg['Text']
    if "##" in msg_str and msg['FromUserName'] == global_params["admin_user_username"] and msg['ToUserName'] == global_params["admin_user_username"]:
        for command in admin_command_dict.keys():
            if command in msg_str:
                admin_command_dict[command](msg)
                return True
    if "#" in msg_str:
        for command in command_dict.keys():
            if command in msg_str:
                command_dict[command](msg)
                return True
    return False