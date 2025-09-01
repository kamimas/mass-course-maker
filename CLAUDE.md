# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python automation tool for creating courses from PDF materials using the Penseum.dev API. The main script (`mass_course_creator.py`) handles the complete workflow of uploading PDFs, creating courses, and publishing them.

## Core Architecture

The application is built around the `PenseumCourseCreator` class which manages:
- API authentication with JWT tokens
- Material upload workflow
- Course creation and configuration
- Course publishing pipeline

### Key Workflow
1. Login to Penseum API and obtain JWT token
2. Upload PDF materials from `studocu` folder
3. Create courses with 10-minute daily limits
4. Update course names based on filenames
5. Publish courses

## Development Setup

Install dependencies:
```bash
pip install -r requirements.txt
```

Run the application:
```bash
python mass_course_creator.py
```

## Project Structure

- `mass_course_creator.py` - Main application script containing the complete workflow
- `requirements.txt` - Python dependencies (requests, pathlib2)
- `studocu/` - Expected folder containing PDF materials (referenced in workspace but external)
- `mass-course-maker.code-workspace` - VS Code workspace configuration

## API Integration

The application integrates with Penseum API v3 endpoints:
- `/user/login` - Authentication
- `/courses/upload_material` - File upload
- `/courses/create/v3` - Course creation (v3 API)
- `/courses/{id}` - Course updates
- `/courses/{id}/publish` - Course publishing

## Configuration

- Base URL: `https://app.penseum.com/api-handler`
- API Version: v3 for course creation
- Timeout: 150 seconds for course creation
- File types: PDF only
- Authentication: JWT Bearer token
- Course naming: Set via update endpoint after creation (v3 behavior)

## Usage Modes

The script supports three modes:
1. Single file testing - Process one PDF for testing
2. Batch processing - Process all PDFs in studocu folder
3. Manual course creation - Create course from existing material ID