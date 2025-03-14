#!/usr/bin/env python
"""
Verification script for AI Orchestration System
This script checks if all components can be imported correctly
and if the environment is properly configured.
"""

import os
import sys
import logging
import importlib

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("verification.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def check_import(module_name):
    """Try to import a module and return True if successful."""
    try:
        importlib.import_module(module_name)
        logger.info(f"✓ Successfully imported {module_name}")
        return True
    except ImportError as e:
        logger.error(f"✗ Failed to import {module_name}: {str(e)}")
        return False

def check_environment_variables():
    """Check if required environment variables are set."""
    required_vars = [
        "TELEGRAM_TOKEN",
        "OPENAI_API_KEY",
        "GEMINI_API_KEY",
        "GOOGLE_DRIVE_FOLDER_ID"
    ]
    
    all_present = True
    for var in required_vars:
        if os.environ.get(var):
            logger.info(f"✓ Environment variable {var} is set")
        else:
            logger.warning(f"✗ Environment variable {var} is not set")
            all_present = False
    
    return all_present

def check_directory_structure():
    """Check if all required directories exist."""
    required_dirs = [
        "src",
        "src/ai_integration",
        "src/telegram",
        "src/storage",
        "utils",
        "logs"
    ]
    
    all_exist = True
    for directory in required_dirs:
        if os.path.isdir(directory):
            logger.info(f"✓ Directory {directory} exists")
        else:
            logger.warning(f"✗ Directory {directory} does not exist")
            all_exist = False
    
    return all_exist

def main():
    """Run all verification checks."""
    logger.info("Starting verification of AI Orchestration System")
    
    # Check directory structure
    logger.info("\nChecking directory structure:")
    check_directory_structure()
    
    # Check environment variables
    logger.info("\nChecking environment variables:")
    check_environment_variables()
    
    # Check core imports
    logger.info("\nChecking core imports:")
    core_imports = [
        "telegram",
        "openai",
        "google.generativeai",
        "flask",
        "dotenv"
    ]
    
    all_core_imports_successful = True
    for module in core_imports:
        if not check_import(module):
            all_core_imports_successful = False
    
    # Check project-specific imports
    logger.info("\nChecking project imports:")
    try:
        # Add the current directory to the import path
        sys.path.insert(0, os.getcwd())
        
        project_imports = [
            "utils.error_handler",
            "src.ai_integration.ai_orchestrator",
            "src.ai_integration.gemini_connector",
            "src.ai_integration.chatgpt_connector",
            "src.telegram.telegram_bot",
            "src.storage.google_drive_storage"
        ]
        
        all_project_imports_successful = True
        for module in project_imports:
            if not check_import(module):
                all_project_imports_successful = False
        
    except Exception as e:
        logger.error(f"Error during project imports check: {str(e)}")
        all_project_imports_successful = False
    
    # Summary
    logger.info("\nVerification Summary:")
    if all_core_imports_successful:
        logger.info("✓ All core dependencies imported successfully")
    else:
        logger.warning("✗ Some core dependencies failed to import")
    
    if all_project_imports_successful:
        logger.info("✓ All project modules imported successfully")
    else:
        logger.warning("✗ Some project modules failed to import")
    
    if check_environment_variables():
        logger.info("✓ All required environment variables are set")
    else:
        logger.warning("✗ Some environment variables are missing")
    
    if check_directory_structure():
        logger.info("✓ All required directories exist")
    else:
        logger.warning("✗ Some directories are missing")
    
    logger.info("\nVerification completed. Check the details above for any issues.")

if __name__ == "__main__":
    main()
