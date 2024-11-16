from fastapi import FastAPI

app = FastAPI()

# Определение маршрутов
@app.get("/")
async def root():
    return {"message": "Hello World!"}

if __name__ == "__main__":
    app.run()