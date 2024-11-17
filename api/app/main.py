import os
import zipfile
import pandas as pd
import shutil
import hashlib
import time
import uuid

from fastapi import FastAPI, Query, UploadFile, HTTPException
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask
from supabase import create_client
from dotenv import load_dotenv

# загрузка .env
load_dotenv()

app = FastAPI()

DATA_DIR = "./data"
os.makedirs(DATA_DIR, exist_ok=True)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE")
if SUPABASE_KEY is None or SUPABASE_URL is None:
    raise RuntimeError("Environment variables for Supabase was not found")

supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
BUCKET_NAME = "sprint-data"

def generate_unique_prefix():
    """Creates a unique prefix based on current time"""
    current_time = str(time.time()).encode()
    return hashlib.md5(current_time).hexdigest()[:8]


def process_csv_file(file_path: str) -> str | None:
    try:
        df = pd.read_csv(file_path, sep=";", skiprows=1)
        print(f"Loaded DataFrame for {file_path}, shape: {df.shape}")

        if df.empty:
            print(f"File {file_path} is empty after processing. Skipping.")
            return None

        # считаем дубликаты
        duplicate_count = int(df.duplicated().sum())
        print(f"Duplicates found in {file_path}: {duplicate_count}")

        # удаляем полные дубликаты
        df = df.drop_duplicates()

        # сохраняем обработанный .csv с разделителем ","
        processed_file_path = file_path.replace(".csv", "_processed.csv")
        df.to_csv(processed_file_path, index=False, sep=",")
        print(f"Processed file saved: {processed_file_path}")

        return processed_file_path
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return None


def process_csv_files_in_zip(input_zip_path: str, output_zip_path: str) -> dict:
    temp_dir = os.path.join(DATA_DIR, f"temp_{uuid.uuid4().hex}")
    duplicate_counts = {}
    try:
        os.makedirs(temp_dir, exist_ok=True)
        print(f"Temporary directory created: {temp_dir}")

        # распаковка
        with zipfile.ZipFile(input_zip_path, "r") as zip_ref:
            zip_ref.extractall(temp_dir)
            print(f"Files in ZIP archive: {zip_ref.namelist()}")
            print(f"Unzipped to: {temp_dir}")

        output_files = []
        for root, _, files in os.walk(temp_dir):
            for file_name in files:
                print(f"Found file: {file_name}")
                if file_name.endswith(".csv"):
                    file_path = os.path.join(root, file_name)
                    try:
                        df = pd.read_csv(file_path, sep=";", skiprows=1)
                        print(f"Loaded DataFrame for {file_name}, shape: {df.shape}")

                        if df.empty:
                            print(
                                f"File {file_name} is empty after processing. Skipping."
                            )
                            continue

                        # считаем дубликаты
                        duplicate_count = int(df.duplicated().sum())
                        duplicate_counts[file_name] = duplicate_count

                        # удаляем полные дубликаты
                        df = df.drop_duplicates()

                        # сохраняем обработанный .csv с разделителем ";"
                        processed_file_name = f"processed_{file_name}"
                        output_file_path = os.path.join(root, processed_file_name)
                        df.to_csv(output_file_path, index=False, sep=",")
                        output_files.append(output_file_path)
                        print(f"Processed file saved: {output_file_path}")
                    
                    except Exception as e:
                        print(f"Error processing file {file_name}: {e}")
                        continue

        # проверяем что обработанные файлы .csv существуют
        if not output_files:
            print("No valid CSV files found for processing.")
            raise RuntimeError(
                "No valid CSV files found for processing in the ZIP archive."
            )

        # запаковываем для отправки
        with zipfile.ZipFile(output_zip_path, "w") as zipf:
            for file in output_files:
                arch_name = os.path.relpath(file, temp_dir)
                zipf.write(file, arch_name)
                print(f"Added '{file}' to ZIP as '{arch_name}'")

        return duplicate_counts

    except zipfile.BadZipFile:
        raise RuntimeError("The uploaded file is not a valid ZIP archive.")
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise RuntimeError(f"Unexpected error during ZIP processing: {e}")
    finally:
        # удаляем временные файлы
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
            print(f"Cleaned up temporary directory: {temp_dir}")


def download_from_supabase(
    remote_file_path: str,
    local_path: str,
    bucket_name: str
):
    response = supabase_client.storage.from_(
        bucket_name
    ).download(remote_file_path)
    
    with open(local_path, "wb") as f:
        f.write(response)

    print("Supabase file saved at:", local_path)
    print(f"Downloaded ZIP saved to: {local_path}")


def upload_to_supabase(local_path: str, remote_file_name: str, bucket_name: str):
    with open(local_path, "rb") as f:
        upload_response = supabase_client.storage.from_(bucket_name).upload(
            remote_file_name, f
        )
    
    if upload_response.get("error") is not None:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload processed file to Supabase Storage: {upload_response['error']}",
        )
    
    supabase_file_url = (
        f"{SUPABASE_URL}/storage/v1/object/public/{bucket_name}/{remote_file_name}"
    )
    print(f"Processed file uploaded to Supabase Storage: {supabase_file_url}")
    return supabase_file_url


def download_and_process_folder_from_supabase(
    bucket_name: str,
    folder_path: str
) -> list:
    temp_dir = os.path.join(DATA_DIR, f"temp_{uuid.uuid4().hex}")
    os.makedirs(temp_dir, exist_ok=True)
    print(f"Temporary directory created for download: {temp_dir}")

    files = supabase_client.storage.from_(bucket_name).list(folder_path)
    uploaded_files_urls = []

    for item in files:
        if not item["name"].endswith("/") and item["name"].endswith(".csv"):
            file_path = os.path.join(folder_path, item["name"])
            local_file_path = os.path.join(temp_dir, item["name"])
            local_file_dir = os.path.dirname(local_file_path)
            os.makedirs(local_file_dir, exist_ok=True)
            download_from_supabase(file_path, local_file_path, bucket_name)

            # Process the downloaded CSV file
            processed_file_path = process_csv_file(local_file_path)
            if processed_file_path:
                remote_file_name = f"processed/{uuid.uuid4().hex}/{os.path.basename(processed_file_path)}"
                uploaded_files_urls.append(upload_to_supabase(processed_file_path, remote_file_name, bucket_name))

    # cleaning up
    shutil.rmtree(temp_dir, ignore_errors=True)
    print(f"Cleaned up temporary directory for download: {temp_dir}")

    return uploaded_files_urls

@app.post("/process-zip-file/")
async def process_zip_file(file: UploadFile):
    if file.filename is None:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file must have a name"
        )

    if not file.filename.endswith(".zip"):
        raise HTTPException(
            status_code=400,
            detail="Uploaded file must be a ZIP file"
        )

    unique_prefix = generate_unique_prefix()
    input_zip_path = os.path.join(DATA_DIR, f"{unique_prefix}_input.zip")
    output_zip_path = os.path.join(DATA_DIR, f"{unique_prefix}_output.zip")

    try:
        # сохраняем
        with open(input_zip_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print(f"Uploaded ZIP saved to: {input_zip_path}")

        # обрабатываем zip
        try:
            duplicated = process_csv_files_in_zip(input_zip_path, output_zip_path)
        except Exception as e:
            print(f"Error during processing: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Error processing file: {str(e)}"
            )

        # проверяем что был создан обработанный файл
        if not os.path.exists(output_zip_path):
            print(f"Output ZIP file was not created: {output_zip_path}")
            raise HTTPException(
                status_code=500,
                detail=f"Output ZIP file was not created: {output_zip_path}",
            )

        print(f"Duplicates removed: {duplicated}")
        print(f"Returning output ZIP file: {output_zip_path}")
        return FileResponse(
            output_zip_path,
            filename=f"processed_{file.filename}",
            background=BackgroundTask(
                lambda: cleanup_files(input_zip_path, output_zip_path)
            ),
        )
    finally:
        # Clean up input and output files after response is sent
        def cleanup_files(input_zip, output_zip):
            if os.path.exists(input_zip):
                os.remove(input_zip)
                print(f"Removed input file: {input_zip}")
            if os.path.exists(output_zip):
                os.remove(output_zip)
                print(f"Removed output file: {output_zip}")


@app.post("/process-zip-supabase/")
async def process_zip_supabase(
    folder_path: str = Query(...),
    bucket_name: str = Query(...)
):
    try:
        # Download and process folder from Supabase Storage
        uploaded_files_urls = download_and_process_folder_from_supabase(
            bucket_name,
            folder_path
        )

        return {"file_urls": uploaded_files_urls}
    finally:
        pass


@app.get("/sprint-data")
async def get_sprint_data():
    return {
        "sprint": "Спринт 2024.3.6.NPP Shared Sprint",
        "total_estimate": 146,
        "real_estimate": 100,
        "tasks_count": 58,
        "done_tasks_count": 39,
        "removed_tasks_count": 5,
        "backlogged_tasks_count": 4,
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
        }
    }


# curl -X POST "http://127.0.0.1:8000/process-zip-supabase/" -H "Content-Type: application/json" -d '{"folder_path": "f124eb6b-b478-43ae-b084-00e73af53c7c/upload_01/", "bucket_name": "sprint-data"}'
