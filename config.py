# config.py
import os

# ---------- пути к файлам ----------
FILTERED_KERNEL_DIR = "logs"
FILTERED_KERNEL_LOG = os.path.join(FILTERED_KERNEL_DIR, "filtered_kernel.log")

def get_files_path(logs_dir):
    return {
        "kernel_log"  : os.path.join(logs_dir, "SIMULATION/kernel.log"),
        "traffic_log" : os.path.join(logs_dir, "SIMULATION/traffic.log"),
        "gis_log"     : os.path.join(logs_dir, "SIMULATION/gis.log"),
    }

JSON_DIR = "json_files"
LOCATIONS_JSON = os.path.join(JSON_DIR, "locations.json")
TRAFFIC_JSON = os.path.join(JSON_DIR, "traffic.json")
STATIC_OBJECTS_JSON = os.path.join(JSON_DIR, "static_objects.json")
ID_TO_TYPE_JSON = os.path.join(JSON_DIR, "id_to_type.json")
VISION_JSON = os.path.join(JSON_DIR, "vision.json")
RESULT_DATASET_JSON = os.path.join(JSON_DIR, "dataset.json")

DATASET_DIR = "dataset"
DATASET_CSV = os.path.join(DATASET_DIR, "dataset.csv")

# ---------- параметры датасета ----------
WINDOW_SIZE = 10
MAX_OBJECTS = 30
CLUSTER_DIST_AGENT = 2.0  # метры
CLUSTER_DIST_STATIC = 5.0

# ---------- справочники ----------
TYPE2ID = {
    "Building": 1, "Road": 2, "Refuge": 3, "Hydrant": 4,
    "Fire station": 5, "Police office": 6, "Ambulance centre": 7,
    "Civilian": 8, "Ambulance team": 9, "Police force": 10, "Fire brigade": 11,
}
ACTION2ID = {
    "rest": 1, "move": 2, "load": 3, "unload": 4,
    "rescue": 5, "clear": 6, "extinguish": 7,
}

AGENT_TYPES = ["Civilian", "Police force", "Ambulance team", "Fire brigade"]
AGENT_TYPES_WITHOUT_CIVILIAN = ["Police force", "Ambulance team", "Fire brigade"]

PRIORITIES = {
    "Fire brigade": ["Hydrant", "Fire station", "Building", "Agent", "Road"],
    "Police force": ["Road", "Police office", "Agent"],
    "Ambulance team": ["Agent", "Refuge", "Ambulance center", "Building", "Road"],
}

# ---------- целевой агент по умолчанию ----------
DEFAULT_AGENT_ID = "80713181"
DEFAULT_TARGET_ID = "243740087"
DEFAULT_TARGET_TYPE = "Fire brigade"
