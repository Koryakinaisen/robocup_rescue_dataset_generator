# data_pipeline/parse_locations.py
import json
import re
from config import KERNEL_LOG, LOCATIONS_JSON

def _parse_log_to_json(log_file_path, json_file_path):
    """
    Парсим kernel.log, извлекая инфу о видимых агентах
    (time, id, type, locationX, locationY).
    """
    # Регулярные выражения для поиска нужных строк
    timestep_pattern = re.compile(r"INFO kernel : Timestep (\d+)\s*$")
    # Например, "Finding visible entities for Civilian (706111255)"
    visible_entity_pattern = re.compile(r"DEBUG kernel : Finding visible entities for ([\w\s]+) \((\d+)\)")
    # Например, "Finding visible entities from 235218.0 , 118346.0"
    visible_from_pattern = re.compile(r"DEBUG kernel : Finding visible entities from ([\d\.]+)\s*,\s*([\d\.]+)")

    # Результат будет списком словарей, каждый из которых соответствует временной метке
    result = []
    current_time_dict = None

    # Открываем лог файл и построчно его обрабатываем
    with open(log_file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        # Если встретили строку с временной меткой
        time_match = timestep_pattern.match(line)
        if time_match:
            # Если уже есть данные для предыдущего временного шага – сохраняем их
            if current_time_dict is not None:
                result.append(current_time_dict)
            # Создаём новый словарь для текущей временной метки
            current_time_dict = {"time": time_match.group(1), "data": []}
            i += 1
            continue

        # Если строка содержит информацию о видимости агента
        visible_match = visible_entity_pattern.match(line)
        if visible_match:
            agent_type = visible_match.group(1).strip()  # сохраняем тип агента
            agent_id = visible_match.group(2).strip()  # сохраняем id агента
            # Следующая строка должна содержать координаты
            i += 1
            if i < len(lines):
                line_next = lines[i].strip()
                from_match = visible_from_pattern.match(line_next)
                if from_match:
                    locationX = from_match.group(1)
                    locationY = from_match.group(2)
                    # Если уже определена временная метка, добавляем запись
                    if current_time_dict is not None:
                        current_time_dict["data"].append({
                            "id": agent_id,
                            "type": agent_type,
                            "locationX": locationX,
                            "locationY": locationY
                        })
            i += 1
            continue

        # Если строка не соответствует ни одному из шаблонов, переходим к следующей
        i += 1

    # Добавляем последний собранный блок, если он существует
    if current_time_dict is not None:
        result.append(current_time_dict)

    # Сохраняем результат в JSON файл с форматированием
    with open(json_file_path, 'w', encoding='utf-8') as out_file:
        json.dump(result, out_file, indent=2, ensure_ascii=False)

    print(f"[parse_locations] Данные сохранены в {json_file_path}")


def generate_locations_file():
    """
    Запускаем парсер для kernel.log -> locations.json
    """
    _parse_log_to_json(KERNEL_LOG, LOCATIONS_JSON)
