# job_automation.py
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from resume_generator import ResumeGenerator
from field_detector import FieldDetector

class JobAutomation:
    def __init__(self):
        self.driver = webdriver.Chrome()
        with open("site_selectors.json") as f:
            self.selectors = json.load(f)
        self.resume_gen = ResumeGenerator()
        self.field_detector = FieldDetector()
    
    def apply_to_job(self, job_url):
        # Step 1: Detect job portal
        portal = self._detect_portal(job_url)
        print(f"Detected portal: {portal}")
        
        # Step 2: Login if needed
        if portal == "linkedin":
            self._linkedin_login()
        
        # Step 3: Get job details
        self.driver.get(job_url)
        time.sleep(3)
        job_description = self._scrape_job_description()
        
        # Step 4: Generate documents
        job_analysis = self.resume_gen.analyze_job_description(job_description)
        resume = self.resume_gen.tailor_resume(job_analysis)
        cover_letter = self.resume_gen.generate_cover_letter(job_description)
        
        # Step 5: Handle multi-step forms
        self._handle_multi_step_form(portal, resume, cover_letter)
        
        # Cleanup
        time.sleep(5)
        self.driver.quit()
    
    def _handle_multi_step_form(self, portal, resume, cover_letter):
        step = 1
        while True:
            print(f"Processing step {step}...")
            
            # Step 5.1: Detect and fill fields in the current step
            field_mapping = self.field_detector.detect_form_fields(self.driver)
            self._fill_application_form(field_mapping)
            
            # Step 5.2: Upload documents if applicable
            if step == 1:  # Assume documents are uploaded in the first step
                self._upload_documents(portal, resume, cover_letter)
            
            # Step 5.3: Check for a "Next" button
            try:
                next_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Next')]")
                next_button.click()
                time.sleep(2)  # Wait for the next step to load
                step += 1
            except NoSuchElementException:
                print("No more steps found. Proceeding to submit.")
                break
        
        # Step 5.4: Submit the final form
        self._submit_application(portal)
    
    def _fill_application_form(self, field_mapping):
        info = self.resume_gen.user_data["personal"]
        
        for label, field in field_mapping.items():
            try:
                # Find the input field associated with the label
                input_field = self.driver.find_element(By.XPATH, f"//label[contains(text(), '{label}')]/following-sibling::input")
                input_field.send_keys(info[field])
                time.sleep(0.5)
            except NoSuchElementException:
                print(f"Field not found: {label}")
    
    def _upload_documents(self, portal, resume, cover_letter):
        selectors = self.selectors.get(portal, {}).get("application", self.selectors["common"])
        
        # Save files temporarily
        with open("temp_resume.pdf", "w") as f:
            f.write(resume)
        with open("temp_cl.txt", "w") as f:
            f.write(cover_letter)
        
        # Upload files
        try:
            upload = selectors["resume_upload"]
            self.driver.find_element(
                getattr(By, upload["by"].upper()), 
                upload["value"]
            ).send_keys("temp_resume.pdf")
        except NoSuchElementException:
            print("Resume upload field not found")
    
    def _submit_application(self, portal):
        selectors = self.selectors.get(portal, {}).get("application", self.selectors["common"])
        try:
            submit_btn = selectors["submit"]
            self._find_element(submit_btn).click()
        except NoSuchElementException:
            print("Submit button not found")
    
    def _find_element(self, selector):
        return self.driver.find_element(
            getattr(By, selector["by"].upper()),
            selector["value"]
        )
    
    def _scrape_job_description(self):
        # Try to extract job description from common elements
        try:
            return self.driver.find_element(By.CSS_SELECTOR, ".job-description").text
        except NoSuchElementException:
            try:
                return self.driver.find_element(By.CSS_SELECTOR, ".description").text
            except NoSuchElementException:
                return "Job description not found"

if __name__ == "__main__":
    automator = JobAutomation()
    automator.apply_to_job("https://www.linkedin.com/jobs/view/1234567890")
