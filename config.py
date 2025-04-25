# config.py
import os

# ---------- пути к файлам ----------
LOGS_DIR = "logs"
KERNEL_LOG = os.path.join(LOGS_DIR, "kernel.log")
TRAFFIC_LOG = os.path.join(LOGS_DIR, "traffic.log")
GIS_LOG = os.path.join(LOGS_DIR, "gis.log")
FILTERED_KERNEL_LOG = os.path.join(LOGS_DIR, "filtered_kernel.log")
MAP_GML_FILE = os.path.join(LOGS_DIR, "map.gml")

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
    "Fire station": 5, "Police office": 6, "Ambulance center": 7,
    "Civilian": 8, "Ambulance team": 9, "Police force": 10, "Fire brigade": 11,
}
ACTION2ID = {
    "rest": 1, "move": 2, "load": 3, "unload": 4,
    "rescue": 5, "clear": 5, "extinguish": 6,
}

AGENT_TYPES = ["Civilian", "Police force", "Ambulance team", "Fire brigade"]

PRIORITIES = {
    "Fire brigade": ["Hydrant", "Fire station", "Building", "Agent", "Road"],
    "Police force": ["Road", "Police office", "Agent"],
    "Ambulance team": ["Agent", "Refuge", "Ambulance center", "Building", "Road"],
}

# ---------- целевой агент по умолчанию ----------
DEFAULT_AGENT_ID = "80713181"
DEFAULT_TARGET_ID = "243740087"
DEFAULT_TARGET_TYPE = "Fire brigade"
