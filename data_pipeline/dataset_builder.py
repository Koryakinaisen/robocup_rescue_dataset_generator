# data_pipeline/dataset_builder.py
"""
Собирает JSON-датасет: берём окна из VISION_JSON, обогащаем
данными из traffic/locations, затем сокращаем каждый снапшот
до MAX_OBJECTS согласно таблицам приоритетов (PRIORITIES).
"""

import json
import math

from config import (
    WINDOW_SIZE, MAX_OBJECTS,
    AGENT_TYPES, PRIORITIES, RESULT_DATASET_JSON
)

CLUSTER_DISTANCE_AGENTS = 2.0
CLUSTER_DISTANCE_STATIC_OBJECTS = 5.0


def dist(obj_a, obj_b):
    return math.hypot(obj_a["locationX"] - obj_b["locationX"],
                      obj_a["locationY"] - obj_b["locationY"])

def find_object_by_id(data, search_id):
    for item in data:
        if item['id'] == search_id:
            return item
    return None

def get_target_agent_action():
    pass


def did_agent_moved(agent_id, current_time, predict_time, locations):
    if current_time <= 1:
        return False
    obj_in_past = find_object_by_id(locations[predict_time - WINDOW_SIZE - current_time]['data'], agent_id)
    obj_now = find_object_by_id(locations[predict_time - WINDOW_SIZE - current_time + 1]['data'], agent_id)
    if not obj_now or not obj_in_past:
        return False
    if obj_in_past['locationX'] == obj_now['locationX'] and obj_in_past['locationY'] == obj_now['locationY']:
        return False
    return True

def category(obj):
    """Сводим детальные типы к укрупнённым категориям,
    чтобы ими было удобно пользоваться в таблице приоритетов."""
    return "Agent" if obj["type"] in AGENT_TYPES else obj["type"]


def cluster_objects(objects, target, order, target_id):
    """
    Выполняет приоритетную кластеризацию:
    идём по категориям (приоритетам) и в каждой оставляем
    по одному представителю из &laquo;скученных&raquo; групп.
    """
    clustered = []

    # Выбираем подходящую дистанцию кластеризации для каждой категории
    def thr(cat):
        return CLUSTER_DISTANCE_AGENTS if cat == "Agent" else CLUSTER_DISTANCE_STATIC_OBJECTS

    for cat in order:
        # Фильтруем объекты текущей категории (без целевого агента, он отдельно)
        cand = [o for o in objects if category(o) == cat and o["id"] != target_id]
        # Сортируем кандидатов по расстоянию к целевому, ближайшие — первыми
        cand.sort(key=lambda o: dist(o, target) if target else 0)

        kept = []
        for obj in cand:
            if any(dist(obj, k) < thr(cat) for k in kept):
                continue             # слишком близко к уже сохранённому
            kept.append(obj)
        clustered.extend(kept)

    # Все категории, которых нет в order, обрабатываем в конце без приоритета
    rest = [o for o in objects if category(o) not in order and o["id"] != target_id]
    clustered.extend(rest)
    return clustered

def priority_idx(obj, order):
    try:
        return order.index(category(obj))
    except ValueError:
        return len(order)      # то, что не перечислено, уходит в конец


def calculate_centroid(obj):
    if obj.get('type', '') in AGENT_TYPES:
        return obj.get('coordinates').get('locationX'), obj.get('coordinates').get('locationY')
    # Извлекаем список координатных сегментов из объекта
    coordinates = obj.get('coordinates', [])

    # Собираем все уникальные начальные точки каждого сегмента
    points = [segment[0] for segment in coordinates]

    # Вычисляем сумму координат X и Y
    sum_x = sum(point['locationX'] for point in points)
    sum_y = sum(point['locationY'] for point in points)

    # Количество точек
    count = len(points)

    # Рассчитываем центроид
    centroid_x = sum_x / count
    centroid_y = sum_y / count

    return round(centroid_x, 3), round(centroid_y, 3)


def get_from_traffic(agent_id, curr_index, predict_time, traffic, locations):
    buried = False
    injured = False
    dead = False
    curr_time = predict_time - WINDOW_SIZE + curr_index
    agent_action = 'move' if did_agent_moved(agent_id, curr_time, predict_time, locations) else 'rest'
    for agent in traffic[curr_time - 1]['agents']:
        if agent['id'] == agent_id:
            if agent['action'] == 'buried':
                buried = True
                continue
            if agent['action'] == 'injured':
                injured = True
                continue
            if agent['action'] == 'dead':
                dead = True
                continue
            if agent['action'].startswith('at') or agent['action'].startswith('in'):
                continue
            if agent['action'].startswith('load'):
                agent_action = 'load'
                continue
            if agent['action'].startswith('unload'):
                agent_action = 'unload'
                continue
            if agent['action'] == 'rescuing':
                agent_action = 'rescue'
                continue
            if agent['action'] == 'clearing':
                agent_action = 'clear'
                continue
            if agent['action'] == 'extinguishing':
                agent_action = 'extinguish'

    return buried, injured, dead, agent_action


def filter_snapshot(snapshot, target_id, target_type):
    """Сокращает список snapshot['data'] согласно правилам."""
    items = snapshot["data"]
    target = next((o for o in items if o["id"] == target_id), None)

    # Если объектов и так не больше лимита — ничего не сокращаем
    if len(items) < MAX_OBJECTS or (len(items) == MAX_OBJECTS and target):
        return snapshot

    # --- Запускаем кластеризацию/сокращение ---
    order = PRIORITIES[target_type]

    # 1. Кластеризуем все объекты по приоритетам
    clustered = cluster_objects(items, target, order, target_id)

    # 2. Сортируем итоговый список по (приоритет, расстояние)
    def s_key(o):
        return (priority_idx(o, order),
                dist(o, target) if target else 0)

    clustered.sort(key=s_key)
    target_second_check = next((o for o in clustered if o["id"] == target_id), None)
    limit = MAX_OBJECTS - 1 if not target or not target_second_check else MAX_OBJECTS
    clustered = clustered[:limit]

    snapshot["data"] = clustered
    return snapshot


def process_log(timeline, target_id, target_type):
    return [filter_snapshot(snap, target_id, target_type) for snap in timeline]


def get_obj_in_vision(predict_time, vision, traffic, locations):
    dataset = []
    for current_index in range(WINDOW_SIZE):
        data = []
        for obj in vision[current_index]['vision']:
            locationX, locationY = calculate_centroid(obj)
            is_buried, is_injured, is_dead, action = get_from_traffic(obj['id'], current_index, predict_time, traffic, locations)
            OBJ = {
                'id': obj['id'],
                'type': obj['type'],
                'locationX': locationX,
                'locationY': locationY,
            }
            if OBJ['type'] in AGENT_TYPES:
                OBJ['isBuried'] = is_buried
                OBJ['isInjured'] = is_injured
                OBJ['isDead'] = is_dead
                OBJ['action'] = action
            # Добавить для зданий ignition

            data.append(OBJ)
        dataset.append({
            'time': predict_time - WINDOW_SIZE + current_index,
            'data': data
        })
    return dataset


def build_dataset_json(target_id, predict_time, id_to_type, vision, traffic, locations):
    json_file = get_obj_in_vision(predict_time, vision, traffic, locations)
    target_type = id_to_type.get(target_id, '')
    new_json = process_log(json_file, target_id, target_type)
    # with open(RESULT_DATASET_JSON, 'w', encoding='utf-8') as out:
    #     json.dump(new_json, out, indent=2, ensure_ascii=False)
    # print(f"[dataset_builder] Датасет сохранён в {RESULT_DATASET_JSON}")
    for elem in new_json:
        if len(elem['data']) > MAX_OBJECTS:
            raise ValueError(f"There are more than {MAX_OBJECTS} objects after filtering.")
    return new_json