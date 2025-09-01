#!/usr/bin/env python3
"""
Test script for testing single course creation with the new API v3
"""

from mass_course_creator import PenseumCourseCreator
from pathlib import Path

def test_single_course():
    creator = PenseumCourseCreator()
    
    print("🧪 Testing API v3 with single course creation")
    print("=" * 50)
    
    # Check if studocu folder exists
    studocu_path = Path("studocu")
    if not studocu_path.exists():
        print("❌ studocu folder not found!")
        print("   Please create a 'studocu' folder and add some PDF files for testing")
        return False
    
    # Find PDF files
    pdf_files = list(studocu_path.glob("*.pdf"))
    if not pdf_files:
        print("❌ No PDF files found in studocu folder!")
        print("   Please add some PDF files to the studocu folder")
        return False
    
    test_file = pdf_files[0]
    print(f"📄 Found test file: {test_file.name}")
    
    # Test login first
    print("\n🔐 Testing authentication...")
    if not creator.login():
        print("❌ Login failed! Check credentials and API endpoint")
        return False
    
    # Test the complete workflow
    print(f"\n🚀 Testing course creation workflow with: {test_file.name}")
    success = creator.create_course_from_file(str(test_file))
    
    if success:
        print("\n🎉 SUCCESS! API v3 is working correctly")
    else:
        print("\n❌ FAILED! There might be issues with the API v3 implementation")
    
    return success

if __name__ == "__main__":
    test_single_course()