def page_2(name_file, id_sprint):
    sprint_table = pd.read_csv(name_file, sep=';',skiprows=1)
    data = pd.read_csv(name_file, skiprows=1, sep = ';')

    df_sprint = data[data['entity_id'].isin(id_sprint)].reset_index(drop=True)

    task_chel_pt = df_sprint.pivot_table(index=['assignee'], values=['estimation','spent'], aggfunc='sum')
    task_chel_pt = task_chel_pt[task_chel_pt['estimation']>0]

    task_chel_pt['estimation'] = (task_chel_pt['estimation']/3600).round().astype('Int64')
    task_chel_pt['spent'] = (task_chel_pt['spent']/3600).round().astype('Int64')

    task_chel_pt['stat'] = task_chel_pt["estimation"] - task_chel_pt["spent"]

    task_chel_pt['procent'] = (((task_chel_pt['spent'] - task_chel_pt['estimation']) / task_chel_pt['estimation']) * 100).round(0)

    def categorize(row):
        if row['estimation'] == row['stat']:
            return -1
        difference = row['spent'] - row['estimation']
        percentage_diff = (difference / row['estimation']) * 100
        if abs(percentage_diff) == 0:
            return 0
        elif abs(percentage_diff) <= 10:
            return 10 if percentage_diff > 0 else -10
        elif abs(percentage_diff) <= 20:
            return 20 if percentage_diff > 0 else -20
        elif abs(percentage_diff) <= 60:
            return 60 if percentage_diff > 0 else -60
        else:
            return 100 if percentage_diff > 0 else -100
        
    task_chel_pt["Category"] = task_chel_pt.apply(categorize, axis=1)

    task = task_chel_pt.to_numpy()
    empl = task_chel_pt.index
    rez = []
    for i in range(len(task)):
        newEl = {
            'assignee':empl[i],
            'estimation':	task[i][0],
            'spent':task[i][1],
            'stat':	task[i][2],
            'procent':task[i][3],
            'category':task[i][4]
        }
        rez.append(newEl)
    return rez