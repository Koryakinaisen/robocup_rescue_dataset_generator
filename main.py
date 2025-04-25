# main.py
import os
import json

from data_pipeline.log_filter import filter_kernel_log
from data_pipeline.parse_static_objects import generate_static_objects_file
from data_pipeline.parse_locations import generate_locations_file
from data_pipeline.parse_traffic import generate_traffic_file
from data_pipeline.parse_agent_types import generate_id_to_type
from data_pipeline.agent_selector import choose_agent
from data_pipeline.target_selector import choose_target
from data_pipeline.vision_merger import merge_vision_data
from data_pipeline.dataset_builder import build_dataset_json
from data_pipeline.csv_converter import convert_dataset_to_csv

from config import (
    ID_TO_TYPE_JSON, VISION_JSON, TRAFFIC_JSON, LOCATIONS_JSON, STATIC_OBJECTS_JSON,
)


def _load_data():
    with open(ID_TO_TYPE_JSON, 'r') as f:
        id_to_type = json.load(f)
    with open(TRAFFIC_JSON, 'r') as f:
        traffic = json.load(f)
    with open(LOCATIONS_JSON, 'r') as f:
        locations = json.load(f)
    with open(STATIC_OBJECTS_JSON, 'r') as f:
        static_objects = json.load(f)
    return id_to_type, traffic, locations, static_objects


def main():
    # # 1. фильтруем kernel.log
    # filter_kernel_log()
    # # 2. создаём вспомогательные JSON-ы
    # generate_static_objects_file()
    # generate_locations_file()
    # generate_traffic_file()
    # generate_id_to_type()
    # 3. выбираем актёров
    agent_id = choose_agent()
    target_id = choose_target()
    # 4. сливаем данные о &laquo;зрении&raquo;
    id_to_type, traffic, locations, static_objects = _load_data()
    current_time = 100
    vision = merge_vision_data(agent_id, current_time, locations, static_objects)


    # 5. строим датасет с приоритетной фильтрацией
    timestamp = build_dataset_json(target_id, current_time + 1, id_to_type, vision, traffic, locations)
    # 6. конвертируем в CSV
    convert_dataset_to_csv(timestamp, target_id, 'Fire brigade')
    print("=== pipeline завершён ===")


if __name__ == "__main__":
    os.makedirs("dataset", exist_ok=True)
    main()
