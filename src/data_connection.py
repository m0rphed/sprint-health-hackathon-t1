import csv
import os

class DateTime:
    def __init__(self) -> None:
        self.year = 0
        self.month = 0
        self.day = 0
        self.hour = 0
        self.minute = 0
        self.second = 0
        self.m_second = 0
    def __init__(self, datetime: str):
        t_datetime = datetime.split(' ')
        t_date = t_datetime[0].split('-')
        t_time = t_datetime[1].split(':')
        self.year = int(t_date[0])
        self.month = int(t_date[1])
        self.day = int(t_date[2])
        self.hour = int(t_time[0])
        self.minute = int(t_time[1])
        self.second = int(t_time[2].split('.')[0])
        self.m_second = int(t_time[2].split('.')[1])

    def get_date(self, delimiter='/'):
        return f"{self.year}{delimiter}{self.month}{delimiter}{self.day}"
    
        """ self > datetime => 1
            self < datetime => -1
            self = datetime => 0
        """    
    def compare(self, datetime) -> int:
        res = [attr for attr in dir(self) 
                if not callable(getattr(self, attr)) 
                and not attr.startswith('_')]
        for r in res:
            if getattr(self, r) > getattr(datetime, r): return 1
            elif getattr(self, r) < getattr(datetime, r): return -1
            else: continue
        return 0

class Task:
    fields = ["entity_id",
              "area",
              "type",
              "status",
              "state",
              "priority",
              "ticket_number",
              "name",
              "create_date",
              "created_by",
              "update_date",
              "updated_by",
              "parent_ticket_id",
              "assignee",
              "owner",
              "due_date",
              "rank",
              "estimation",
              "spent",
              "workgroup",
              "resolution"]
    def __init__(self, data):
        self.data = data

    def get_id(self):
        return self.data[Task.fields[0]]
        
        


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

