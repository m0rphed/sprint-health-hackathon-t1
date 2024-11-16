from fastapi import FastAPI, Request, UploadFile

app = FastAPI()

# Определение маршрутов
@app.get("/root")
async def root():
    return {"message": "Hello World!"}

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