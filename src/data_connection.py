import csv
import os

class DataConnection:
    # Если что сюда вместо моего пути засуньте свой, либо же при инициализации объекта напишите свой путь в виде list
    def __init__(self, filename=[".\\..\\TestData\\Tasks.csv",
                                 ".\\..\\TestData\\History.csv",
                                 ".\\..\\TestData\\Sprints.csv"]):
        self.files = filename # хранится массив путей к файлам
        self.data = {} # хранятся строки в виде словаря

    def open_files(self):
        for file_id in range(0, len(self.files)):
            with open(self.files[file_id], 'r') as csvfile:
                reader = csv.DictReader(csvfile, delimiter=';')
                self.data[os.path.basename(self.files[file_id])] = [row for row in reader]

