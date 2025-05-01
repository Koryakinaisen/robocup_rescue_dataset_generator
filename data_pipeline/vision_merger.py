# data_pipeline/vision_merger.py
import re

from config import FILTERED_KERNEL_LOG, AGENT_TYPES


def _get_coordinates(roads_locations, buildings_locations, locations_data, target_type, target_id, time_idx):
    """
    Ищем координаты в статичных объектах (Building/Road) или в locations.json.
    """
    coordinates = None
    if target_type in AGENT_TYPES:
        for item in locations_data[time_idx].get("data"):
            if item.get("id") == target_id:
                coordinates = {
                    "locationX": float(item.get("locationX")) / 1000,
                    "locationY": float(item.get("locationY")) / 1000
                }
                break
        return coordinates
    if target_type == 'Road':
        for item in roads_locations:
            if item.get("id") == target_id:
                coordinates = item.get("coordinates")
                break
        return coordinates
    for item in buildings_locations:
        if item.get("id") == target_id:
            coordinates = item.get("coordinates")
            break

    return coordinates



def merge_vision_data(target_id, current_time, locations_data, static_objects):
    """
    Пример чтения отфильтрованного лога (filtered_kernel.log),
    вычленения записей, где Ambulance/Police/Fire brigade что-то видят,
    и сохранения в vision.json.
    Параллельно пытаемся искать координаты видимых объектов.
    """
    roads_locations = static_objects['roads']
    buildings_locations = static_objects['buildings']

    # Список, куда будем складывать результаты
    results = []

    # Регулярное выражение для разбора строки лога
    pattern = re.compile(
        r'^DEBUG kernel :\s+(Ambulance team|Police force|Fire brigade)\s+\((\d+)\)\s+can\s+see\s+\[(.*)\]',
        re.IGNORECASE
    )
    timestep_pattern = re.compile(r"INFO kernel : Timestep (\d+)\s*$")
    needed_timestep = current_time - 9
    timestep = 0
    # Открываем лог-файл
    with open(FILTERED_KERNEL_LOG, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            time_match = timestep_pattern.match(line)
            if time_match:
                timestep = int(time_match.group(1))
                continue
            if timestep < needed_timestep:
                continue
            if timestep > current_time:
                break
            match = pattern.match(line)
            if match:
                team, team_id, vision_data = match.groups()
                # Проверяем, что id совпадает с заранее известным
                if team_id != target_id:
                    continue

                # vision_data содержит строку типа:
                # "Building (18208), Ambulance team (1839229664), Road (8610), ..."
                # Разбиваем строку по запятой
                items = [item.strip() for item in vision_data.split(",")]
                vision = []
                # Регулярное выражение для каждого элемента
                item_pattern = re.compile(r'([\w\s]+)\s+\((\d+)\)')
                for item in items:
                    item_match = item_pattern.search(item)
                    if item_match:
                        obj_type, obj_id = item_match.groups()
                        obj_coordinates = _get_coordinates(
                            roads_locations,
                            buildings_locations,
                            locations_data,
                            obj_type,
                            obj_id,
                            timestep)
                        if obj_coordinates is not None:
                            vision.append({
                                "type": obj_type.strip(),
                                "id": obj_id.strip(),
                                "coordinates": obj_coordinates
                            })

                results.append({
                    "timestep": timestep,
                    "vision": vision
                })


    # with open(VISION_JSON, "w", encoding="utf-8") as outfile:
    #     json.dump(results, outfile, indent=4, ensure_ascii=False)

    # print(f"[vision_merger] Результат сохранён в {VISION_JSON}")
    return results
