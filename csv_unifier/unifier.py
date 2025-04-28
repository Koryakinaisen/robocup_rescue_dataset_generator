import csv
import random

# Список путей к CSV-файлам
file_paths = [
    "D:\RoboCup LOGS\log-TK24-Day2_RC23_bordeaux2\DATASET\dataset.csv",
    "D:\RoboCup LOGS\log-Ri-one-Day2_RC23_paris1\DATASET\dataset.csv",
    "D:\RoboCup LOGS\log-Ri-one-Day2_RC23_eindhoven2\DATASET\dataset.csv",
    "D:\RoboCup LOGS\log-AIT-Rescue-Day2_RC23_mexico2\DATASET\dataset.csv",
    "D:\RoboCup LOGS\log-AIT-Rescue_B-Day2_RC23_vc2\DATASET\dataset.csv",
    "D:\RoboCup LOGS\log-AIT-Rescue_B-Day2_RC23_kobe2\DATASET\dataset.csv"
]

header = None  # Заголовок CSV
all_rows = []  # Все строки данных

# Чтение и объединение файлов
for idx, path in enumerate(file_paths):
    with open(path, "r", newline="") as file:
        reader = csv.reader(file)

        # Обработка заголовка (только для первого файла)
        if idx == 0:
            header = next(reader)

        # Пропуск заголовка в остальных файлах
        else:
            next(reader)

        # Добавление строк в общий список
        all_rows.extend(list(reader))

# Перемешивание строк
random.shuffle(all_rows)

# Запись результата в новый файл
with open("dataset.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(header)  # Запись заголовка
    writer.writerows(all_rows)  # Запись перемешанных данных