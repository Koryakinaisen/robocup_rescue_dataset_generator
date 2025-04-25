# data_pipeline/parse_agent_types.py
import re
import json

from config import GIS_LOG, ID_TO_TYPE_JSON

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


def generate_id_to_type():
    """
    Парсим gis.log и записываем соответствие id->type в JSON.
    """
    id_to_type = _parse_gis_log(GIS_LOG)
    with open(ID_TO_TYPE_JSON, 'w') as json_file:
        json.dump(id_to_type, json_file, indent=4)

    print(f"[parse_agent_types] Словарь id -> type сохранен в {ID_TO_TYPE_JSON}")