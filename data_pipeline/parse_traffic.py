# data_pipeline/parse_traffic.py
import json
import re
from config import TRAFFIC_LOG, TRAFFIC_JSON

def _parse_traffic_log(log_file_path, json_file_path):
    """
    Парсим traffic.log, собирая действия агентов на каждом Timestep.
    """
    # Регулярное выражение для поиска строки с таймстепом: "INFO ... : Timestep X"
    timestep_pattern = re.compile(r'INFO traffic3\.simulator\.TrafficSimulator : Timestep (\d+)$')
    # Регулярное выражение для поиска строки действия агента:
    # "DEBUG ... : Agent Civilian (755181377) is buried"
    agent_pattern = re.compile(
        r'^DEBUG\s+[\w.]+\s+:\s+(?:Agent\s+)?([A-Za-z]+(?: [A-Za-z]+)*)\s+\((\d+)\)\s+is\s+(.*)$')
    # Регулярное выражение для  поиска строки действия скорой
    ambulance_pattern = re.compile(r'^DEBUG\s+[\w.]+\s+:\s+Ambulance team\s+\((\d+)\)\s+((?:unloaded|loaded).*)$')

    timesteps = []  # Список со всеми таймстепами
    current_time = None  # Текущий таймстеп
    current_agents = []  # Список агентов для текущего таймстепа

    with open(log_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Проверяем, не встретили ли мы строку с новым таймстепом
            match_timestep = timestep_pattern.search(line)
            if match_timestep:
                # Если у нас уже был какой-то таймстеп, сохраняем его в список
                if current_time is not None:
                    timesteps.append({
                        "time": current_time,
                        "agents": current_agents
                    })
                # Обновляем текущий таймстеп и список агентов
                current_time = match_timestep.group(1)
                current_agents = []
                continue

            # Проверяем, не встретили ли мы строку с действием агента
            match_agent = agent_pattern.search(line)
            if match_agent and current_time is not None:
                agent_type = match_agent.group(1)
                agent_id = match_agent.group(2)
                agent_action = match_agent.group(3)
                current_agents.append({
                    "id": agent_id,
                    "type": agent_type,
                    "action": agent_action
                })
                continue

            match_ambulance = ambulance_pattern.search(line)
            if match_ambulance and current_time is not None:
                agent_type = "Ambulance team"
                agent_id = match_ambulance.group(1)
                agent_action = match_ambulance.group(2)
                current_agents.append({
                    "id": agent_id,
                    "type": agent_type,
                    "action": agent_action
                })

    # Если файл закончился, а данные по последнему таймстепу не добавлены — добавляем
    if current_time is not None:
        timesteps.append({
            "time": current_time,
            "agents": current_agents
        })

    # Сохраняем результат в JSON-файл
    with open(json_file_path, 'w', encoding='utf-8') as out:
        json.dump(timesteps, out, indent=2, ensure_ascii=False)

    print(f"[parse_traffic] Файл {json_file_path} успешно создан.")

def generate_traffic_file():
    """
    Запуск парсера traffic.log -> traffic.json
    """
    _parse_traffic_log(TRAFFIC_LOG, TRAFFIC_JSON)