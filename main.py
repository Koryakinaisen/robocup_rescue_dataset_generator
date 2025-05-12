# main.py
import os
import json
import argparse
import zipfile
import tempfile
import tarfile
import lzma
import shutil
from pathlib import Path

from data_pipeline.log_filter import filter_kernel_log
from data_pipeline.parse_static_objects import generate_static_objects_file
from data_pipeline.parse_locations import generate_locations_file
from data_pipeline.parse_traffic import generate_traffic_file
from data_pipeline.parse_agent_types import generate_id_to_type, delete_unused_agents
from data_pipeline.agent_selector import choose_agent
from data_pipeline.target_selector import choose_target
from data_pipeline.vision_merger import merge_vision_data
from data_pipeline.dataset_builder import build_dataset_json
from data_pipeline.csv_converter import convert_dataset_to_csv

from config import (
    ID_TO_TYPE_JSON, TRAFFIC_JSON, LOCATIONS_JSON, STATIC_OBJECTS_JSON,
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


def extract_archive(archive_path: str) -> str:
    """
    Распаковывает ZIP / TAR (tar.gz, tar.bz2, tar.xz, …) /
    одиночные XZ-файлы.  Возвращает путь к каталогу с данными.
    """
    archive_path = Path(archive_path)
    temp_dir = Path(tempfile.mkdtemp(prefix="robocup_logs_"))

    try:
        # -------- ZIP ------------------------------------------------------
        if archive_path.suffix == ".zip":
            with zipfile.ZipFile(archive_path) as zf:
                zf.extractall(temp_dir)

        # -------- TAR.* (tar, tar.gz, tar.bz2, tar.xz, …) ------------------
        elif tarfile.is_tarfile(archive_path):
            # 'r:*' = autodetect сжатия (gz, bz2, xz, zstd, none)
            with tarfile.open(archive_path, mode="r:*") as tf:
                tf.extractall(temp_dir)

        # -------- &laquo;голый&raquo; .xz (один-единственный файл) ---------------------
        elif archive_path.suffix == ".xz":
            dest = temp_dir / archive_path.with_suffix("").name
            with lzma.open(archive_path) as src, open(dest, "wb") as dst:
                shutil.copyfileobj(src, dst)

        else:
            raise RuntimeError(f"Неизвестный формат: {archive_path.suffix}")

        # --- если архив содержал единственный каталог, возвращаем его ------
        items = list(temp_dir.iterdir())
        if len(items) == 1 and items[0].is_dir():
            return str(items[0])

        return str(temp_dir)

    except Exception as exc:
        # если хочется бросать своё исключение
        raise RuntimeError(f"Не удалось распаковать {archive_path}: {exc}") from exc

    except Exception as e:
        shutil.rmtree(temp_dir)  # Удаляем временную директорию при ошибке
        raise RuntimeError(f"Failed to extract {archive_path}: {str(e)}")


def main():
    # Распаковываем архив
    parser = argparse.ArgumentParser(description='Process RoboCup logs.')
    parser.add_argument('--archive', help='Path to the logs archive (ZIP)')
    parser.add_argument('--map', help='Path to the map (GML)')
    args = parser.parse_args()

    if args.archive:
        logs_dir = extract_archive(args.archive)
    if args.map:
        map_path = args.map

    if not os.path.exists(logs_dir):
        raise FileNotFoundError(f"Logs directory not found: {logs_dir}")
    if not os.path.exists(map_path):
        raise FileNotFoundError(f"Map file not found: {map_path}")

    # фильтруем kernel.log
    filtered_kernel = filter_kernel_log(logs_dir)

    # создаём вспомогательные JSON-ы
    static_objects = generate_static_objects_file(map_path)
    locations = generate_locations_file(logs_dir)
    traffic = generate_traffic_file(logs_dir)
    id_to_type = generate_id_to_type(logs_dir, locations)

    # получаем список агентов наблюдателей
    agent_id_s = choose_agent(id_to_type, locations)

    for agent_observer in agent_id_s:
        current_time = int(agent_observer.get('time', 0))

        agent_id = agent_observer.get('id', None)

        # Получаем обзор агента наблюдателя
        vision = merge_vision_data(filtered_kernel, agent_id, current_time, locations, static_objects)

        # Выбираем агента, которого будем прогнозировать
        target_agent = choose_target(agent_id, vision, traffic, locations, current_time)
        if not target_agent or agent_id == target_agent.get('id', None):
            continue
        target_id = target_agent.get('id', None)
        target_type = target_agent.get('type', None)
        target_action = target_agent.get('action', None)

        # Фильтруем обзор агента наблюдателя
        timestamp = build_dataset_json(target_id, current_time + 1, id_to_type, vision, traffic, locations)

        # Записываем данные в csv файл
        convert_dataset_to_csv(timestamp, target_id, target_type, target_action)


if __name__ == "__main__":
    os.makedirs("dataset", exist_ok=True)
    main()
