import google.generativeai as genai
import cv2
import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

# Configure the API key
genai.configure(api_key=os.getenv('gemini_key'))

# Initialize the model
model = genai.GenerativeModel('gemini-1.5-flash')



def process_csv(csv_path):
    error_messages = []
    result_text = ""

    try:
 
        # Upload the image file
        csv_file = genai.upload_file(path=csv_path, display_name="Consolidated Report")
        print(f"Uploaded file '{csv_file.display_name}' as: {csv_file.uri}")

        # Prompt the model to find expiry date, manufacture date, and batch number
        prompt = (
            "This is an consolidated report of grocery items"
            "find patterns or trends in data"
            "Respond back in Markdown format"
        )

        # Generate content using the model
        response = model.generate_content([csv_file, prompt])
        result_text = response.text

    except Exception as e:
        error_messages.append(f"An unexpected error occurred: {e}")
    finally:
        # Clean up: remove the temporary file
        if 'csv_path' in locals() and os.path.exists(csv_path):
            os.remove(csv_path)

    # Print any error messages or the result
    if error_messages:
        for error in error_messages:
            print(f"Error: {error}")
            return None
    else:
        print("Result:")
        print(result_text)
        return result_text
      
