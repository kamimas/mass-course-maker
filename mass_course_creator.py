#!/usr/bin/env python3
"""
Mass Course Creator for Penseum.dev API
Automates the process of creating courses from PDF materials in the studocu folder.
"""

import os
import requests
import json
from pathlib import Path
import time
from typing import Optional, Dict, Any

class PenseumCourseCreator:
    def __init__(self):
        self.base_url = "https://app.penseum.com/api-handler"
        self.jwt_token = None
        self.headers = {
            "accept": "application/json",
            "content-type": "application/json"
        }
        
        # Login credentials
        self.email = "kamyar@digitaldashdev.com"
        self.password = "12345678Aa!"
        
        # Course settings
        self.daily_minute = 10  # Daily limit as requested
        
    def login(self) -> bool:
        """Authenticate and get JWT token"""
        login_url = f"{self.base_url}/user/login"
        login_data = {
            "email": self.email,
            "password": self.password
        }
        
        try:
            response = requests.post(login_url, json=login_data, headers=self.headers)
            response.raise_for_status()
            
            result = response.json()
            self.jwt_token = result.get("access_token")
            
            if self.jwt_token:
                self.headers["Authorization"] = f"Bearer {self.jwt_token}"
                print("✅ Successfully logged in and obtained JWT token")
                return True
            else:
                print("❌ Login failed: No access_token in response")
                print(f"Response: {result}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Login failed: {e}")
            return False
    
    def upload_material(self, file_path: str) -> Optional[str]:
        """Upload a material file and return the material_id"""
        upload_url = f"{self.base_url}/courses/upload_material"
        
        try:
            with open(file_path, 'rb') as file:
                files = {'file': (os.path.basename(file_path), file, 'application/pdf')}
                
                # Remove content-type header for file upload
                upload_headers = {k: v for k, v in self.headers.items() if k != "content-type"}
                
                response = requests.post(upload_url, files=files, headers=upload_headers)
                response.raise_for_status()
                
                result = response.json()
                material_id = result.get("material_id")
                
                if material_id:
                    print(f"✅ Successfully uploaded {os.path.basename(file_path)}")
                    print(f"   Material ID: {material_id}")
                    return material_id
                else:
                    print(f"❌ Upload failed: No material_id in response")
                    print(f"Response: {result}")
                    return None
                    
        except requests.exceptions.RequestException as e:
            print(f"❌ Upload failed for {file_path}: {e}")
            return None
        except FileNotFoundError:
            print(f"❌ File not found: {file_path}")
            return None
    
    def create_course(self, material_id: str, course_name: str = None) -> Optional[str]:
        """Create a course with the uploaded material"""
        create_url = f"{self.base_url}/courses/create/v3"
        
        course_data = {
            "material_id_list": [material_id]
        }
        
        # Note: Course name will be set via update endpoint after creation in v3
        
        try:
            print("⏳ Creating course (this may take up to 2 minutes)...")
            # Set timeout to 150 seconds since API can take longer than expected
            response = requests.post(create_url, json=course_data, headers=self.headers, timeout=150)
            response.raise_for_status()
            
            result = response.json()
            course_id = result.get("course_id")
            
            if course_id:
                print(f"✅ Successfully created course")
                print(f"   Course ID: {course_id}")
                if course_name:
                    print(f"   Course Name: {course_name}")
                return course_id
            else:
                print(f"❌ Course creation failed: No course_id in response")
                print(f"Response: {result}")
                return None
                
        except requests.exceptions.Timeout:
            print(f"⏰ Course creation timed out after 150 seconds")
            print(f"   The course might still be processing on the server")
            print(f"   Material ID: {material_id} (save this for reference)")
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Course creation failed: {e}")
            return None
    
    def update_course_name(self, course_id: str, new_name: str) -> bool:
        """Update the course name"""
        update_url = f"{self.base_url}/courses/{course_id}"
        
        update_data = {
            "new_name": new_name
        }
        
        try:
            response = requests.patch(update_url, json=update_data, headers=self.headers)
            response.raise_for_status()
            
            print(f"✅ Successfully updated course name to: {new_name}")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Course name update failed: {e}")
            return False
    
    def publish_course(self, course_id: str) -> bool:
        """Publish the created course"""
        publish_url = f"{self.base_url}/courses/{course_id}/publish"
        
        try:
            response = requests.post(publish_url, headers=self.headers)
            response.raise_for_status()
            
            print(f"✅ Successfully published course {course_id}")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Course publishing failed: {e}")
            return False
    
    def create_course_from_file(self, file_path: str) -> bool:
        """Complete workflow: upload file, create course, update name, and publish"""
        print(f"\n🚀 Processing: {os.path.basename(file_path)}")
        print("-" * 50)
        
        # Generate course name from filename
        filename = os.path.basename(file_path)
        course_name = os.path.splitext(filename)[0].replace("_", " ").replace("-", " ")
        
        # Step 1: Upload material
        material_id = self.upload_material(file_path)
        if not material_id:
            return False
        
        # Step 2: Create course
        course_id = self.create_course(material_id, course_name)
        if not course_id:
            return False
        
        # Step 3: Update course name
        name_updated = self.update_course_name(course_id, course_name)
        if not name_updated:
            print("⚠️  Course created but name update failed, continuing with publish...")
        
        # Step 4: Publish course
        success = self.publish_course(course_id)
        
        if success:
            print(f"🎉 Successfully created and published course: {course_name}")
        
        return success
    
    def test_single_course(self):
        """Test the workflow with a single file from studocu folder"""
        studocu_path = Path("studocu")
        
        if not studocu_path.exists():
            print("❌ studocu folder not found!")
            return False
        
        # Find the first PDF file
        pdf_files = list(studocu_path.glob("*.pdf"))
        if not pdf_files:
            print("❌ No PDF files found in studocu folder!")
            return False
        
        test_file = pdf_files[0]
        print(f"🧪 Testing with file: {test_file.name}")
        
        # Login first
        if not self.login():
            return False
        
        # Process the test file
        return self.create_course_from_file(str(test_file))
    
    def process_all_courses(self):
        """Process all PDF files in the studocu folder"""
        studocu_path = Path("studocu")
        
        if not studocu_path.exists():
            print("❌ studocu folder not found!")
            return
        
        pdf_files = list(studocu_path.glob("*.pdf"))
        if not pdf_files:
            print("❌ No PDF files found in studocu folder!")
            return
        
        print(f"📚 Found {len(pdf_files)} PDF files to process")
        
        # Login first
        if not self.login():
            return
        
        successful = 0
        failed = 0
        
        for pdf_file in pdf_files:
            try:
                if self.create_course_from_file(str(pdf_file)):
                    successful += 1
                else:
                    failed += 1
                
                # Add a small delay between requests to be respectful
                time.sleep(2)
                
            except KeyboardInterrupt:
                print("\n⏹️  Process interrupted by user")
                break
            except Exception as e:
                print(f"❌ Unexpected error processing {pdf_file.name}: {e}")
                failed += 1
        
        print(f"\n📊 Summary:")
        print(f"   ✅ Successful: {successful}")
        print(f"   ❌ Failed: {failed}")
        print(f"   📁 Total: {len(pdf_files)}")

    def manual_course_creation(self):
        """Manually create a course using an existing material ID"""
        if not self.login():
            return
        
        material_id = input("Enter material ID: ").strip()
        if not material_id:
            print("❌ No material ID provided")
            return
        
        course_name = input("Enter course name (optional): ").strip()
        course_name = course_name if course_name else None
        
        course_id = self.create_course(material_id, course_name)
        if course_id:
            if course_name:
                name_updated = self.update_course_name(course_id, course_name)
                if not name_updated:
                    print("⚠️  Course created but name update failed, continuing with publish...")
            
            success = self.publish_course(course_id)
            if success:
                print(f"🎉 Successfully created and published course!")
        else:
            print("❌ Failed to create course")

def main():
    creator = PenseumCourseCreator()
    
    print("🎓 Penseum Mass Course Creator")
    print("=" * 40)
    
    while True:
        print("\nOptions:")
        print("1. Test with single course")
        print("2. Process all courses")
        print("3. Manual course creation (use existing material ID)")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            creator.test_single_course()
        elif choice == "2":
            confirm = input("⚠️  This will process ALL PDF files. Continue? (y/N): ").strip().lower()
            if confirm == 'y':
                creator.process_all_courses()
        elif choice == "3":
            creator.manual_course_creation()
        elif choice == "4":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-4.")

if __name__ == "__main__":
    main() 