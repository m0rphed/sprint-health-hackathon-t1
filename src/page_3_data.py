import data_connection as dc

data_con = dc.DataConnection()

data_con.open_files()
#print(data_con.get_by_id(1805925, "tasks"))
#temp = data_con.get_sprint_tasks(len(data_con.sprints)-1)
#print(temp)
temp1 = data_con.get_history_for_sprint(len(data_con.sprints)-1)
print(temp1)