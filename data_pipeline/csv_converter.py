# data_pipeline/csv_converter.py
import csv
import os

from pathlib import Path
from config import (
    DATASET_CSV,
    WINDOW_SIZE,
    MAX_OBJECTS,
    TYPE2ID,
    ACTION2ID,
)
FEATURES = [
    "type",        # 1‑е число в блоке
    "locationX",   # 2‑е
    "locationY",   # 3‑е
    "isVisible",   # 4‑е
    "isTarget",    # 5‑е
    "feature1",    # 6‑е
    "feature2",    # 7‑е
    "feature3",    # 8‑е
    "feature4",    # 9‑е
]

EMPTY_OBJ = [0, -1, -1, 0, 0, 0, 0, 0, 0]

def list_to_csv( numbers, target_action, path):
    numbers = list(numbers)
    if len(numbers) != 2700:
        raise ValueError("Numbers must have 2700 elements")
    action_id = ACTION2ID.get(target_action, 0)
    if action_id == 0:
        raise ValueError("Invalid action")
    numbers.append(action_id)
    p = Path(path)
    p.parent.mkdir(exist_ok=True)
    exists = p.exists() and os.path.getsize(p)>0
    with p.open('a' if exists else 'w', newline='', encoding='utf-8') as f:
        w=csv.writer(f)
        # if not exists:
        #     header=[]
        #     for _ in range(WINDOW_SIZE*MAX_OBJECTS): header.extend(FEATURES)
        #     w.writerow(header)
        w.writerow(numbers)


def get_target_action():
    pass


def get_max_locations(data):
    max_location_x = 0
    max_location_y = 0
    for elem in data:
        for obj in elem['data']:
            if obj['locationX'] > max_location_x:
                max_location_x = obj['locationX']
            if obj['locationY'] > max_location_y:
                max_location_y = obj['locationY']
    return max_location_x, max_location_y


def get_obj_vect(obj, location_x_normalizer, location_y_normalizer, target_id):
    is_visible = True
    if obj['locationX'] == -1 or obj['locationY'] == -1:
        is_visible = False
    is_target = 1 if obj['id'] == target_id else 0
    v = [
        TYPE2ID.get(obj['type'], 0),
        round(obj.get("locationX", -1) if not is_visible else obj.get("locationX", 0) / location_x_normalizer, 3),
        round(obj.get("locationY", -1) if not is_visible else obj.get("locationY", 0) / location_y_normalizer, 3),
        int(is_visible),
        int(is_target),
        int(obj.get("isBuried", 0)),
        int(obj.get("isInjured", 0)),
        int(obj.get("isDead", 0)),
        ACTION2ID.get(obj.get("action"), 0),
    ]
    if v[0] == 0 and is_visible:
        print(obj['type'])
        raise TypeError("Type is unknown")
    return v


def check_target(snap, target_id, target_type):
    for i in range(len(snap)):
        if snap[i]['id'] == target_id:
            snap[i], snap[0] = snap[0], snap[i]
            return snap
    target_obj = {
        "id": target_id,
        "type": target_type,
        "locationX": -1,
        "locationY": -1,
    }
    snap.insert(0, target_obj)
    return snap


def pad_objects(snap):
    while len(snap) < MAX_OBJECTS * len(FEATURES):
        snap.extend(EMPTY_OBJ)
    return snap


def get_vect_for_one_time(snap, timestamp, target_id, target_type):
    res = []
    snap = check_target(snap, target_id, target_type)
    max_location_x, max_location_y = get_max_locations(timestamp)
    for obj in snap:
        res.extend(get_obj_vect(obj, max_location_x, max_location_y, target_id))
    return pad_objects(res)


def get_data_in_string(data_list, target_id, target_type):
    res = []
    for snap in data_list:
        arr = get_vect_for_one_time(snap['data'], data_list, target_id, target_type)
        if len(arr) > 270:
            raise ValueError("len arr greater than 270")
        res.extend(arr)
    return res


def convert_dataset_to_csv(timestamp, target_id, target_type, target_action):
    list_to_csv(get_data_in_string(timestamp, target_id, target_type), target_action, DATASET_CSV)