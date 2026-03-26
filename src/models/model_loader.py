"""
模型加载器
通用的模型加载工具
"""

import os
import torch
from pathlib import Path
from typing import Any, Optional, Dict
from loguru import logger


class ModelLoader:
    """模型加载器"""

    def __init__(self, cache_dir: str = "models/cache/"):
        """
        初始化模型加载器

        Args:
            cache_dir: 缓存目录
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.loaded_models: Dict[str, Any] = {}

        logger.info("模型加载器初始化完成")

    def load_model(
        self,
        model_name: str,
        model_path: str,
        device: str = "cuda"
    ) -> Optional[Any]:
        """
        加载模型

        Args:
            model_name: 模型名称
            model_path: 模型路径
            device: 设备

        Returns:
            加载的模型
        """
        if model_name in self.loaded_models:
            logger.info(f"模型 {model_name} 已加载")
            return self.loaded_models[model_name]

        try:
            # 确定设备
            device = device if torch.cuda.is_available() else "cpu"

            logger.info(f"加载模型: {model_name} from {model_path}")

            # 加载模型（通用实现）
            model = torch.load(model_path, map_location=device)

            self.loaded_models[model_name] = model

            logger.info(f"模型 {model_name} 加载成功")

            return model

        except Exception as e:
            logger.error(f"加载模型失败: {e}")
            return None

    def unload_model(self, model_name: str):
        """
        卸载模型

        Args:
            model_name: 模型名称
        """
        if model_name in self.loaded_models:
            del self.loaded_models[model_name]
            logger.info(f"模型 {model_name} 已卸载")

            # 清理GPU缓存
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

    def unload_all(self):
        """卸载所有模型"""
        self.loaded_models.clear()
        logger.info("所有模型已卸载")

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    def get_loaded_models(self) -> list:
        """
        获取已加载的模型列表

        Returns:
            模型名称列表
        """
        return list(self.loaded_models.keys())

    def is_model_loaded(self, model_name: str) -> bool:
        """
        检查模型是否已加载

        Args:
            model_name: 模型名称

        Returns:
            是否已加载
        """
        return model_name in self.loaded_models
