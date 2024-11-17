from fastapi import FastAPI, Request, UploadFile

app = FastAPI()

# Определение маршрутов
@app.get("/root/page1")
async def root():
    return {"sprint": "Спринт 2024.3.6.NPP Shared Sprint",
            "total_etimate": 146,
            "real_estimate": 100,
            "tasks_count": 58,
            "done_tasks_count": 39,
            "removed_tasks_count": 5,
            "backloged_tasks_count": 4,
            "total_backlog": 39,
            "total_removed": 26,
            "change_by_days": {
                "day1": [47, 0],
                "day2": [8, 3],
                "day3": [12, 1],
                "day4": [3, 5],
                "day5": [2, 4],
                "day6": [0, 0],
                "day7": [0, 0]
            }}

@app.post("/main_page")
async def main_page(request: Request):
    data = await request.json()
    return user_func(data)

@app.post("/upload")
async def uploadfile(files: list[UploadFile]):
    try: 
        for file in files:
            file_path = f".\\..\\TestData\\{file.filename}"
            with open(file_path, "wb") as f:
                f.write(file.file.read())
        return {"message": "Files saved successfully"}
    except Exception as e:
        return {"message": e.args}


if __name__ == "__main__":
    app.run