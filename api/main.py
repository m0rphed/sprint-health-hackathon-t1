import os
import zipfile
import pandas as pd
import shutil
import hashlib
import time
import uuid
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import FileResponse

app = FastAPI()

DATA_DIR = "./data"
os.makedirs(DATA_DIR, exist_ok=True)

def generate_unique_prefix():
    """
    creates a unique prefix based on current time
    """
    
    current_time = str(time.time()).encode()
    return hashlib.md5(current_time).hexdigest()[:8]

def process_csv_files_in_zip(input_zip_path, output_zip_path):
    temp_dir = os.path.join(
        DATA_DIR,
        f"temp_{uuid.uuid4().hex}"
    )
    
    try:
        os.makedirs(temp_dir, exist_ok=True)
        print(f"Temporary directory created: {temp_dir}")

        # Unzip the uploaded zip file
        with zipfile.ZipFile(input_zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
            print(f"Unzipped to: {temp_dir}")

        output_files = []
        for root, _, files in os.walk(temp_dir):
            for file_name in files:
                if file_name.endswith(".csv"):
                    file_path = os.path.join(root, file_name)
                    try:
                        # Read CSV, skip the first row
                        df = pd.read_csv(file_path, sep=";", skiprows=1)
                        
                        # Skip empty DataFrame
                        if df.empty:
                            print(f"File {file_name} is empty after processing. Skipping.")
                            continue
                        
                        # удаляем полные дубликаты
                        df = df.drop_duplicates()

                        # Save the processed CSV with ',' separator
                        processed_file_name = f"processed_{file_name}"
                        output_file_path = os.path.join(root, processed_file_name)
                        df.to_csv(output_file_path, index=False, sep=",")
                        output_files.append(output_file_path)
                        print(f"Processed file saved: {output_file_path}")
                    except Exception as e:
                        print(f"Error processing file {file_name}: {e}")
                        continue

        # Check if there are any processed files
        if not output_files:
            print("No valid CSV files found for processing.")
            raise RuntimeError("No valid CSV files found for processing in the ZIP archive.")

        # Zip the processed files
        with zipfile.ZipFile(output_zip_path, 'w') as zipf:
            for file in output_files:
                arcname = os.path.relpath(file, temp_dir)
                zipf.write(file, arcname)
                print(f"Added {file} to ZIP as {arcname}")

    except zipfile.BadZipFile:
        raise RuntimeError("The uploaded file is not a valid ZIP archive.")
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise RuntimeError(f"Unexpected error during ZIP processing: {e}")
    finally:
        # Clean up temporary directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
            print(f"Cleaned up temporary directory: {temp_dir}")

@app.post("/process-zip/")
async def process_zip(file: UploadFile):
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
        # Save the uploaded file
        with open(input_zip_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print(f"Uploaded ZIP saved to: {input_zip_path}")

        # Process the ZIP
        try:
            process_csv_files_in_zip(input_zip_path, output_zip_path)
        except Exception as e:
            print(f"Error during processing: '{e}'")
            raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

        # Check if the output ZIP file was created
        if not os.path.exists(output_zip_path):
            print(f"Output ZIP file was not created: {output_zip_path}")
            raise HTTPException(status_code=500, detail=f"Output ZIP file was not created: {output_zip_path}")

        print(f"Returning output ZIP file: {output_zip_path}")
        return FileResponse(output_zip_path, filename=f"processed_{file.filename}", background=None)
    finally:
        # Clean up input and output files after response is sent
        def cleanup():
            if os.path.exists(input_zip_path):
                os.remove(input_zip_path)
                print(f"Removed input file: {input_zip_path}")
            if os.path.exists(output_zip_path):
                os.remove(output_zip_path)
                print(f"Removed output file: {output_zip_path}")

        from starlette.background import BackgroundTask
        return FileResponse(output_zip_path, filename=f"processed_{file.filename}", background=BackgroundTask(cleanup))
