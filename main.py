#!/usr/bin/env python
# -*-encoding:utf-8-*-

from globals import *
from msg_box import module_msg_box_init, module_msg_box_run
from anti_revoke import module_anti_revoke_init
from keyword_award import module_keyword_award_init

if __name__ == '__main__':
    module_globals_init()
    module_msg_box_init()
    module_anti_revoke_init()
    module_keyword_award_init()
    module_msg_box_run()