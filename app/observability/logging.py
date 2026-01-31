"""日志模块（简化版）"""

import logging
from typing import Any


def get_logger(name: str) -> logging.Logger:
    """获取日志器"""
    return logging.getLogger(name)


def setup_logging(level: str = "INFO") -> None:
    """配置日志"""
    logging.basicConfig(
        level=getattr(logging, level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


__all__ = [
    "get_logger",
    "setup_logging",
]
