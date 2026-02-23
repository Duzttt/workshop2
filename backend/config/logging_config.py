"""
Logging configuration for FAIX AI Chatbot.

This module provides centralized logging configuration with:
- Structured logging format
- Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- File and console handlers
- Performance monitoring
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Dict, Any, Optional
import sys


def get_logging_config(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    max_file_size: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5,
    console_output: bool = True,
) -> Dict[str, Any]:
    """
    Get logging configuration dictionary.
    
    Args:
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        max_file_size: Maximum size of log file in bytes
        backup_count: Number of backup files to keep
        console_output: Whether to output to console
        
    Returns:
        Dictionary with logging configuration
    """
    # Map string log level to logging constant
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    
    level = level_map.get(log_level.upper(), logging.INFO)
    
    # Configure formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s.%(msecs)03d | %(levelname)-8s | %(name)-20s | %(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configure handlers
    handlers = []
    
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(simple_formatter)
        handlers.append(console_handler)
    
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(detailed_formatter)
        handlers.append(file_handler)
    
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "detailed": {"format": detailed_formatter._fmt, "datefmt": detailed_formatter.datefmt},
            "simple": {"format": simple_formatter._fmt, "datefmt": simple_formatter.datefmt},
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "simple",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "faix_chatbot": {
                "level": log_level,
                "handlers": ["console"],
                "propagate": False,
            },
            "backend": {
                "level": log_level,
                "handlers": ["console"],
                "propagate": False,
            },
        },
        "root": {
            "level": "WARNING",
            "handlers": ["console"],
        },
    }


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    max_file_size: int = 10 * 1024 * 1024,
    backup_count: int = 5,
    console_output: bool = True,
) -> None:
    """
    Setup logging configuration for the application.
    
    Args:
        log_level: Minimum log level
        log_file: Path to log file (optional)
        max_file_size: Maximum size of log file in bytes
        backup_count: Number of backup files to keep
        console_output: Whether to output to console
    """
    # Configure root logger
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    
    level = level_map.get(log_level.upper(), logging.INFO)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s.%(msecs)03d | %(levelname)-8s | %(name)-20s | %(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Add console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(simple_formatter)
        root_logger.addHandler(console_handler)
    
    # Add file handler
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(file_handler)
    
    # Configure specific loggers for different modules
    module_loggers = [
        "backend.chatbot.conversation_manager",
        "backend.chatbot.agents",
        "backend.chatbot.prompt_builder",
        "backend.chatbot.knowledge_base",
        "backend.llm.llm_client",
        "backend.nlp.nlp_intent_classifier",
        "backend.nlp.nlp_semantic_search",
    ]
    
    for module_logger in module_loggers:
        logger = logging.getLogger(module_logger)
        logger.setLevel(level)
        logger.propagate = False
    
    # Log startup message
    logging.info("=" * 70)
    logging.info("FAIX AI Chatbot - Logging System Initialized")
    logging.info(f"Log Level: {log_level}")
    if log_file:
        logging.info(f"Log File: {log_file}")
    logging.info("=" * 70)


def get_performance_logger() -> logging.Logger:
    """
    Get a logger for performance monitoring.
    
    Returns:
        Logger instance for performance metrics.
    """
    logger = logging.getLogger("faix_chatbot.performance")
    return logger


def log_performance_metric(
    operation: str,
    duration: float,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Log a performance metric.
    
    Args:
        operation: Name of the operation
        duration: Duration in seconds
        metadata: Additional metadata to log
    """
    logger = get_performance_logger()
    
    if metadata:
        metadata_str = ", ".join(f"{k}={v}" for k, v in metadata.items())
        logger.info(f"PERF: {operation} took {duration:.3f}s | {metadata_str}")
    else:
        logger.info(f"PERF: {operation} took {duration:.3f}s")


# Pre-configured log levels
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}
