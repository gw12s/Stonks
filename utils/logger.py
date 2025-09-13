"""
Logging setup for the 
 ____  _____ ____  _   _ _  __ ____ 
/ ___|_   _/ __ \| \ | | |/ // ___|
\___ \ | || |  | |  \| | ' / \___ \\
 ___) || || |__| | |\  | . \  ___) |
|____/ |_| \____/|_| \_|_|\_\|____/ 
   
        🚀 GO STONK YOURSELF 📈

Why logging? When your code breaks (and it will), logs tell you exactly what happened!!
Much better than scattered print() statements!
        
"""

import logging
import sys
from pathlib import Path
from config import LOGS_DIR

def setup_logger(name: str = "stonks", level: str = "INFO") -> logging.Logger:
    """
    Set up a logger with both file and console output.
    
    Args:
        name: Logger name (usually module name)
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Don't add handlers if they already exist (prevents duplicates)
    if logger.hasHandlers():
        return logger
    
    logger.setLevel(getattr(logging, level.upper()))
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler - logs everything to file
    file_handler = logging.FileHandler(LOGS_DIR / "stonks.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler - only show INFO and above in terminal
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger