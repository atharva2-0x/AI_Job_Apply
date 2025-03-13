# field_detector.py
import pytesseract
from PIL import Image
import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

class FieldDetector:
    def __init__(self):
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update path

    def extract_text_from_image(self, image_path):
        """Extract text from a screenshot using OCR."""
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text

    def map_labels_to_fields(self, extracted_text):
        """Map extracted labels to user data fields using OpenAI GPT."""
        prompt = f"""
        Map these form labels to user data fields:
        Extracted Labels: {extracted_text}
        User Data Fields: first_name, last_name, email, phone, resume_upload
        Output as JSON: {{"label": "field"}}
        """
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return json.loads(response.choices[0].message.content)

    def detect_form_fields(self, driver):
        """Detect form fields dynamically using AI."""
        # Take a screenshot of the form
        screenshot_path = "form_screenshot.png"
        driver.save_screenshot(screenshot_path)
        
        # Extract text from the screenshot
        extracted_text = self.extract_text_from_image(screenshot_path)
        
        # Map labels to user data fields
        field_mapping = self.map_labels_to_fields(extracted_text)
        return field_mapping
