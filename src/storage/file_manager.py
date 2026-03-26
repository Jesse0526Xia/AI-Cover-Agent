"""
文件管理器
管理音频文件的存储和组织
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from loguru import logger


class FileManager:
    """文件管理器"""

    def __init__(self, base_dir: str = "data/"):
        """
        初始化文件管理器

        Args:
            base_dir: 基础目录
        """
        self.base_dir = Path(base_dir)

        # 创建子目录
        self.audio_dir = self.base_dir / "audio"
        self.output_dir = self.base_dir / "output"
        self.temp_dir = self.base_dir / "temp"

        for dir_path in [self.audio_dir, self.output_dir, self.temp_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"文件管理器初始化完成 - 基础目录: {self.base_dir}")

    def save_audio_file(
        self,
        source_file: str,
        category: str = "audio",
        custom_name: Optional[str] = None
    ) -> str:
        """
        保存音频文件

        Args:
            source_file: 源文件路径
            category: 类别 (audio/output/temp)
            custom_name: 自定义文件名（可选）

        Returns:
            保存后的文件路径
        """
        try:
            # 确定目标目录
            if category == "audio":
                target_dir = self.audio_dir
            elif category == "output":
                target_dir = self.output_dir
            elif category == "temp":
                target_dir = self.temp_dir
            else:
                target_dir = self.base_dir / category
                target_dir.mkdir(parents=True, exist_ok=True)

            # 生成文件名
            if custom_name:
                filename = custom_name
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                ext = Path(source_file).suffix
                filename = f"{timestamp}{ext}"

            # 复制文件
            target_path = target_dir / filename
            shutil.copy2(source_file, target_path)

            logger.info(f"文件保存成功: {target_path}")

            return str(target_path)

        except Exception as e:
            logger.error(f"保存文件失败: {e}")
            raise

    def delete_file(self, file_path: str) -> bool:
        """
        删除文件

        Args:
            file_path: 文件路径

        Returns:
            是否删除成功
        """
        try:
            file_path = Path(file_path)

            if not file_path.exists():
                logger.warning(f"文件不存在: {file_path}")
                return False

            # 删除文件
            file_path.unlink()

            logger.info(f"文件删除成功: {file_path}")

            return True

        except Exception as e:
            logger.error(f"删除文件失败: {e}")
            return False

    def move_file(self, source: str, destination: str) -> bool:
        """
        移动文件

        Args:
            source: 源文件路径
            destination: 目标路径

        Returns:
            是否移动成功
        """
        try:
            source_path = Path(source)
            dest_path = Path(destination)

            if not source_path.exists():
                logger.warning(f"源文件不存在: {source}")
                return False

            # 创建目标目录
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            # 移动文件
            shutil.move(str(source_path), str(dest_path))

            logger.info(f"文件移动成功: {source} -> {destination}")

            return True

        except Exception as e:
            logger.error(f"移动文件失败: {e}")
            return False

    def list_files(
        self,
        category: str = "audio",
        pattern: str = "*"
    ) -> List[str]:
        """
        列出文件

        Args:
            category: 类别
            pattern: 文件匹配模式

        Returns:
            文件路径列表
        """
        try:
            if category == "audio":
                target_dir = self.audio_dir
            elif category == "output":
                target_dir = self.output_dir
            elif category == "temp":
                target_dir = self.temp_dir
            else:
                target_dir = self.base_dir / category

            files = list(target_dir.glob(pattern))
            return [str(f) for f in files]

        except Exception as e:
            logger.error(f"列出文件失败: {e}")
            return []

    def get_file_info(self, file_path: str) -> Optional[dict]:
        """
        获取文件信息

        Args:
            file_path: 文件路径

        Returns:
            文件信息字典
        """
        try:
            file_path = Path(file_path)

            if not file_path.exists():
                return None

            stat = file_path.stat()

            return {
                "name": file_path.name,
                "path": str(file_path),
                "size": stat.st_size,
                "size_mb": stat.st_size / (1024 * 1024),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "extension": file_path.suffix
            }

        except Exception as e:
            logger.error(f"获取文件信息失败: {e}")
            return None

    def cleanup_temp_files(self, max_age_hours: int = 24) -> int:
        """
        清理临时文件

        Args:
            max_age_hours: 最大保留时间（小时）

        Returns:
            清理的文件数量
        """
        try:
            count = 0
            now = datetime.now()

            for file_path in self.temp_dir.glob("*"):
                if file_path.is_file():
                    # 检查文件年龄
                    file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    age_hours = (now - file_time).total_seconds() / 3600

                    if age_hours > max_age_hours:
                        file_path.unlink()
                        count += 1

            logger.info(f"清理临时文件完成 - 删除 {count} 个文件")

            return count

        except Exception as e:
            logger.error(f"清理临时文件失败: {e}")
            return 0

    def get_storage_usage(self) -> dict:
        """
        获取存储使用情况

        Returns:
            存储信息字典
        """
        def get_dir_size(directory):
            total = 0
            for item in directory.glob("*"):
                if item.is_file():
                    total += item.stat().st_size
                elif item.is_dir():
                    total += get_dir_size(item)
            return total

        return {
            "audio_size_mb": get_dir_size(self.audio_dir) / (1024 * 1024),
            "output_size_mb": get_dir_size(self.output_dir) / (1024 * 1024),
            "temp_size_mb": get_dir_size(self.temp_dir) / (1024 * 1024),
            "total_size_mb": get_dir_size(self.base_dir) / (1024 * 1024)
        }
