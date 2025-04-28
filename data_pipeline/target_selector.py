# data_pipeline/target_selector.py
from random import randint

from config import AGENT_TYPES_WITHOUT_CIVILIAN, ACTION2ID


def is_action_move(agent_id, predict_time, locations):
    obj_now = {}
    obj_in_predict = {}
    for location in locations[predict_time - 2].get('data', []):
        if location.get('id', None) == agent_id:
            obj_now = location
    for location in locations[predict_time - 1].get('data', []):
        if location.get('id', None) == agent_id:
            obj_in_predict = location
    if not obj_now or not obj_in_predict:
        return False
    if obj_now['locationX'] == obj_now['locationX'] and obj_in_predict['locationY'] == obj_now['locationY']:
        return False
    return True


def choose_target(vision, traffic, locations,  current_time):
    """
    Заглушка выбора "цели" – в будущем тут может быть логика
    выбора, допустим, самого важного агента/здания и т.д.
    """
    last_vision = vision[-1].get('vision', None)
    agents_in_vision = [item for item in last_vision if item["type"] in AGENT_TYPES_WITHOUT_CIVILIAN]
    if len(agents_in_vision) == 0:
        return 0
    target_index = randint(0, len(agents_in_vision) - 1)
    target_id = agents_in_vision[target_index].get('id', None)
    target_type = agents_in_vision[target_index].get('type', None)
    target_action = 'rest'
    for agent in traffic[current_time].get('agents', []):
        if agent['id'] == target_id:
            if agent['action'] == 'buried':
                continue
            if agent['action'] == 'injured':
                continue
            if agent['action'] == 'dead':
                return None
            if agent['action'].startswith('at') or agent['action'].startswith('in'):
                continue
            if agent['action'].startswith('load'):
                target_action = 'load'
                break
            if agent['action'].startswith('unload'):
                target_action = 'unload'
                break
            if agent['action'] == 'rescuing':
                target_action = 'rescue'
                break
            if agent['action'] == 'clearing':
                target_action = 'clear'
                break
            if agent['action'] == 'extinguishing':
                target_action = 'extinguish'
                break
    if target_action == 'rest' and is_action_move(target_id, current_time + 1, locations):
        target_action = 'move'
    return {
        'id': target_id,
        'type': target_type,
        'action': target_action,
    }