#!/usr/bin/env python
# -*-encoding:utf-8-*-


import json

def load_json_from_file(file_path):
    with open(file_path, 'r', encoding="utf-8") as f:
        load_dict = json.load(f)
    return load_dict
    
def save_json_to_file(file_path, save_dict):
    with open(file_path, 'w', encoding="utf-8") as f:
        json.dump(save_dict, f)


