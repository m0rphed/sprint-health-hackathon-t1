import data_connection as dc

data_con = dc.DataConnection()
datetime_1 = dc.DateTime("2023-12-15 06:09:42.754645")
datetime_2 = dc.DateTime("2023-12-14 06:09:42.754645")
print(datetime_1.compare(datetime_2))