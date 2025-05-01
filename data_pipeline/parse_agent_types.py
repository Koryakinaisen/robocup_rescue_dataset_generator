# data_pipeline/parse_agent_types.py
import re
import json

from config import ID_TO_TYPE_JSON, get_files_path, AGENT_TYPES


def _parse_gis_log(log_file_path):
    """
    Сканируем gis.log, чтобы собрать соответствие id -> тип (Fire brigade, Police force и т.д.).
    Также ищем Refuge (преобразованные Building -> Refuge).
    """
    id_to_type = {}
    # Паттерны для обнаружения строк создания объектов
    created_pattern = re.compile(
        r'DEBUG gis2\.GisScenario : Created (Fire brigade|Police force|Ambulance team|Civilian) \((\d+)\)'
    )
    refuge_pattern = re.compile(
        r'DEBUG gis2\.GisScenario : Converted Building \(\d+\) into Refuge \((\d+)\)'
    )

    with open(log_file_path, 'r') as file:
        for line in file:
            # Проверка на создание обычных объектов
            created_match = created_pattern.search(line)
            if created_match:
                obj_type = created_match.group(1)
                obj_id = int(created_match.group(2))
                id_to_type[obj_id] = obj_type
                continue

            # Проверка на создание Refuge
            refuge_match = refuge_pattern.search(line)
            if refuge_match:
                obj_id = int(refuge_match.group(1))
                id_to_type[obj_id] = 'Refuge'

    return id_to_type


def delete_unused_agents(id_to_type, locations):
    used_ids = set()
    for agent in locations[0]["data"]:
        used_ids.add(agent["id"])

    # 2. Фильтруем словарь по двум условиям
    return {
        agent_id: agent_type
        for agent_id, agent_type in id_to_type.items()
        if agent_id in used_ids and agent_type in AGENT_TYPES
    }


def generate_id_to_type(logs_dir):
    gis_log = get_files_path(logs_dir).get('gis_log')
    """
    Парсим gis.log и записываем соответствие id->type в JSON.
    """
    id_to_type = _parse_gis_log(gis_log)
    with open(ID_TO_TYPE_JSON, 'w') as json_file:
        json.dump(id_to_type, json_file, indent=4)

    print(f"[parse_agent_types] Словарь id -> type сохранен в {ID_TO_TYPE_JSON}")