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
        t_date = [t_datetime[0].split('/')[2], t_datetime[0].split('/')[1], t_datetime[0].split('/')[0]] if '/' in t_datetime[0] else t_datetime[0].split('-')
        t_time = t_datetime[1].split(':') if len(t_datetime)>1 else []
        print(t_date)
        self.year = 0 if len(t_date)<1 else (int(t_date[0]) if(len(t_date[0])==4) else "20" + t_date[0])
        self.month = 0 if len(t_date)<2 else int(t_date[1])
        self.day = 0 if len(t_date)<3 else int(t_date[2])
        self.hour = 0 if len(t_time)<1 else int(t_date[0])
        self.minute = 0 if len(t_time)<2 else int(t_date[1])
        self.second = 0 if len(t_time)<3 else int(t_time[2].split('.')[0])
        self.m_second = 0 if len(t_time)<3 else int(t_time[2].split('.')[1])
        print(self.get_date())

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
        


class DataConnection:
    # Если что сюда вместо моего пути засуньте свой, либо же при инициализации объекта напишите свой путь в виде list
    def __init__(self, filename=[".\\..\\TestData\\Tasks.csv",
                                 ".\\..\\TestData\\History.csv",
                                 ".\\..\\TestData\\Sprints.csv"]):
        self.files = filename # хранится массив путей к файлам
        self.data = {} # хранятся строки в виде словаря
        self.tasks = []
        self.history = []
        self.sprints = []


    def open_files(self):
        for file_id in range(0, len(self.files)):
            with open(self.files[file_id], 'r') as csvfile:
                reader = csv.DictReader(csvfile, delimiter=';')
                self.data[os.path.basename(self.files[file_id])] = [row for row in reader]
        self.tasks = [row for row in self.data["Tasks.csv"][1:]]
        self.history = [row for row in self.data["History.csv"][1:]]
        self.sprints = [row for row in self.data["Sprints.csv"][1:]]        

    def get_by_id(self, obj_id, attr):
        return list(filter(lambda item: int(item["entity_id"]) == obj_id, getattr(self, attr)))[0]

    def get_sprint_tasks(self, sprint_id):
        task_list = [task_id for task_id in list(map(int, self.sprints[sprint_id]["entity_ids"][1:-1].split(',')))]
        tasks = [self.get_by_id(task_id, "tasks") for task_id in task_list]
        return tasks
    
    def get_history_for_sprint(self, sprint_id):
        sprint = self.sprints[sprint_id]
        dates = [DateTime(sprint["sprint_start_date"]), DateTime(sprint["sprint_end_date"])]
        history_clear_list = list(filter(lambda item: item["history_date"] is not None, getattr(self, 'history')))
        #print(history_clear_list[0]["history_date"])
        history_list = list(filter(lambda item: (dates[0].compare(DateTime(item["history_date"])) == -1 and dates[1].compare(DateTime(item["history_date"])) == 1), history_clear_list))
        print(len(history_list))
        return history_list

    def get_history_for_sprint_task(self, sprint_id, task_id):
        pass
