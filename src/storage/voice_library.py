"""
音色仓库
管理音色的存储和检索
"""

import json
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger


class VoiceLibrary:
    """音色仓库"""

    def __init__(self, voices_dir: str = "data/voices/"):
        """
        初始化音色仓库

        Args:
            voices_dir: 音色目录
        """
        self.voices_dir = Path(voices_dir)
        self.voices_dir.mkdir(parents=True, exist_ok=True)

        # 索引文件
        self.index_file = self.voices_dir / "index.json"

        # 加载索引
        self.index = self._load_index()

        logger.info(f"音色仓库初始化完成 - 目录: {self.voices_dir}")

    def _load_index(self) -> Dict[str, Any]:
        """加载索引"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加载索引失败: {e}")

        return {"voices": {}}

    def _save_index(self):
        """保存索引"""
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(self.index, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存索引失败: {e}")

    def add_voice(
        self,
        name: str,
        audio_file: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        添加音色

        Args:
            name: 音色名称
            audio_file: 音频文件路径
            metadata: 元数据（可选）

        Returns:
            是否添加成功
        """
        try:
            voice_dir = self.voices_dir / name

            if voice_dir.exists():
                logger.warning(f"音色 '{name}' 已存在")
                return False

            # 创建音色目录
            voice_dir.mkdir()

            # 复制音频文件
            shutil.copy(audio_file, voice_dir / "reference.wav")

            # 创建元数据
            voice_metadata = {
                "name": name,
                "created_at": datetime.now().isoformat(),
                "audio_file": "reference.wav",
                "status": "ready"
            }

            if metadata:
                voice_metadata.update(metadata)

            # 保存元数据
            with open(voice_dir / "metadata.json", 'w', encoding='utf-8') as f:
                json.dump(voice_metadata, f, ensure_ascii=False, indent=2)

            # 更新索引
            self.index["voices"][name] = voice_metadata
            self._save_index()

            logger.info(f"音色添加成功: {name}")

            return True

        except Exception as e:
            logger.error(f"添加音色失败: {e}")
            return False

    def get_voice(self, name: str) -> Optional[Dict[str, Any]]:
        """
        获取音色信息

        Args:
            name: 音色名称

        Returns:
            音色信息
        """
        return self.index["voices"].get(name)

    def list_voices(self) -> List[Dict[str, Any]]:
        """
        列出所有音色

        Returns:
            音色列表
        """
        return list(self.index["voices"].values())

    def delete_voice(self, name: str) -> bool:
        """
        删除音色

        Args:
            name: 音色名称

        Returns:
            是否删除成功
        """
        try:
            voice_dir = self.voices_dir / name

            if not voice_dir.exists():
                logger.warning(f"音色 '{name}' 不存在")
                return False

            # 删除目录
            shutil.rmtree(voice_dir)

            # 更新索引
            if name in self.index["voices"]:
                del self.index["voices"][name]
                self._save_index()

            logger.info(f"音色删除成功: {name}")

            return True

        except Exception as e:
            logger.error(f"删除音色失败: {e}")
            return False

    def update_voice_metadata(
        self,
        name: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """
        更新音色元数据

        Args:
            name: 音色名称
            metadata: 元数据

        Returns:
            是否更新成功
        """
        try:
            if name not in self.index["voices"]:
                logger.warning(f"音色 '{name}' 不存在")
                return False

            # 更新索引
            self.index["voices"][name].update(metadata)
            self._save_index()

            # 更新文件
            voice_dir = self.voices_dir / name
            metadata_file = voice_dir / "metadata.json"

            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.index["voices"][name], f, ensure_ascii=False, indent=2)

            logger.info(f"音色元数据更新成功: {name}")

            return True

        except Exception as e:
            logger.error(f"更新音色元数据失败: {e}")
            return False

    def search_voices(self, query: str) -> List[Dict[str, Any]]:
        """
        搜索音色

        Args:
            query: 搜索关键词

        Returns:
            匹配的音色列表
        """
        results = []

        for voice in self.index["voices"].values():
            # 在名称和描述中搜索
            if query.lower() in voice.get("name", "").lower():
                results.append(voice)
            elif query.lower() in voice.get("description", "").lower():
                results.append(voice)

        return results

    def get_voice_count(self) -> int:
        """
        获取音色数量

        Returns:
            音色数量
        """
        return len(self.index["voices"])
