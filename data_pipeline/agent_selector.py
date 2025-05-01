# data_pipeline/agent_selector.py
import random

from config import WINDOW_SIZE


def choose_agent(id_to_type, locations):
    """
    Функция выбора наблюдающих агентов каждый момент времени
    """
    start_time = WINDOW_SIZE
    end_time = int(locations[-1].get('time', WINDOW_SIZE))

    target_types = {"Fire brigade", "Ambulance team", "Police force"}
    eligible_agents = [agent_id for agent_id, agent_type in id_to_type.items() if agent_type in target_types]

    group_used = {}
    schedule = []

    for t in range(start_time, end_time):
        group = t // 10
        used = group_used.get(group, set())
        available = [agent_id for agent_id in eligible_agents if agent_id not in used]

        if not available:
            raise ValueError(f"No available agents for time group {group} at time {t}")

        selected = random.choice(available)

        if group not in group_used:
            group_used[group] = set()
        group_used[group].add(selected)

        schedule.append({"time": str(t), "id": selected})

    return schedule