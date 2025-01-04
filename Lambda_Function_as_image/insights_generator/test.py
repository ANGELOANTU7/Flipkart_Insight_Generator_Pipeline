import os
import pandas as pd
import boto3
from io import BytesIO
from submodules.gemini_request import process_csv
from submodules.md_to_pdf import md_to_pdf

def extract_device_and_batch(filename):
    """Extract device_name and batch_no from the filename."""
    base_name = os.path.basename(filename)
    parts = base_name.split("_")
    device_name = parts[0]
    batch_no = parts[1]
    return device_name, batch_no

def download_files_from_s3(bucket_name, s3_prefix, local_dir):
    """Download all .xlsx files from an S3 bucket."""
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION')
    )
    os.makedirs(local_dir, exist_ok=True)  # Ensure local directory exists

    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=s3_prefix)
    if "Contents" in response:
        for obj in response["Contents"]:
            key = obj["Key"]
            if key.endswith(".xlsx"):  # Filter for .xlsx files
                local_file_path = os.path.join(local_dir, os.path.basename(key))
                print(f"Downloading {key} to {local_file_path}")
                s3.download_file(bucket_name, key, local_file_path)
    else:
        print(f"No files found in S3 bucket {bucket_name} with prefix {s3_prefix}")

def process_xlsx_files(input_dir, output_csv):
    """Process all .xlsx files in the directory and create a consolidated CSV."""
    all_data = []

    for file in os.listdir(input_dir):
        if file.endswith(".xlsx"):
            file_path = os.path.join(input_dir, file)
            print(f"Processing file: {file_path}")
            try:
                # Load the .xlsx file
                xls = pd.ExcelFile(file_path)

                # Check if the "Items" sheet exists
                if "Items Sheet" in xls.sheet_names:
                    df = pd.read_excel(xls, sheet_name="Items Sheet")

                    # Extract device_name and batch_no from filename
                    device_name, batch_no = extract_device_and_batch(file)

                    # Add device_name and batch_no columns to the dataframe
                    df["device_name"] = device_name
                    df["batch_no"] = batch_no

                    # Append to the list
                    all_data.append(df)
                else:
                    print(f"'Items Sheet' sheet not found in {file}")
            except Exception as e:
                print(f"Failed to process {file}: {e}")

    # Combine all dataframes
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)

        # Save to CSV
        combined_df.to_csv(output_csv, index=False)
        print(f"Consolidated CSV saved to {output_csv}")
    else:
        print("No valid data found.")

def upload_file_to_s3(file_path, bucket_name, s3_key):
    """Upload file to a specified S3 bucket."""
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION')
    )
    
    try:
        with open(file_path, "rb") as file_data:
            s3.upload_fileobj(file_data, bucket_name, s3_key)
        print(f"File uploaded to S3: s3://{bucket_name}/{s3_key}")
    except Exception as e:
        print(f"Failed to upload file: {e}")

if __name__ == "__main__":
    # S3 bucket details
    bucket_name = "flipkart-reports"  # Replace with your bucket name
    s3_prefix = ""  # Replace with the prefix (folder path in S3)

    # Local directory to temporarily store downloaded files
    local_directory = "temp"

    # Output consolidated CSV file
    output_csv_path = "consolidated_items.csv"

    # Download files from S3
    download_files_from_s3(bucket_name, s3_prefix, local_directory)

    # Process downloaded files
    process_xlsx_files(local_directory, output_csv_path)

    response_md = process_csv(output_csv_path)

    # Generate PDF from markdown
    md_to_pdf(response_md, "temp/insight.pdf")

    # Upload the generated PDF to a different S3 bucket
    pdf_file_path = "temp/insight.pdf"
    s3_bucket_insight = "flipkart-insights"  # Bucket for PDF upload
    s3_pdf_key = "insight.pdf"  # You can adjust the path/key as needed

    # Upload to S3
    upload_file_to_s3(pdf_file_path, s3_bucket_insight, s3_pdf_key)
