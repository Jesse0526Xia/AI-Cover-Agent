"""
音色克隆工具
从音频中提取音色特征并保存到仓库
"""

import os
import shutil
from typing import Dict, Any, Optional
from pathlib import Path
from langchain.tools import Tool
from loguru import logger


class VoiceCloneTool:
    """音色克隆工具"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化音色克隆工具

        Args:
            config: 配置字典
        """
        self.config = config
        self.voices_dir = Path(config.get("storage", {}).get("voices_dir", "data/voices/"))
        self.voices_dir.mkdir(parents=True, exist_ok=True)

        tool_config = config.get("tools", {}).get("voice_clone", {})
        self.enabled = tool_config.get("enabled", True)
        self.min_audio_length = tool_config.get("min_audio_length", 5)
        self.max_audio_length = tool_config.get("max_audio_length", 60)

        logger.info("音色克隆工具初始化完成")

    def clone_voice(
        self,
        audio_file: str,
        voice_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        克隆音色

        Args:
            audio_file: 音频文件路径
            voice_name: 音色名称（可选）

        Returns:
            克隆结果
        """
        logger.info(f"开始克隆音色 - 音频文件: {audio_file}")

        # 验证音频文件
        if not os.path.exists(audio_file):
            return {
                "success": False,
                "message": f"音频文件不存在: {audio_file}"
            }

        # 检查音频长度（这里简化处理，实际应该用librosa检测）
        # audio_length = self._get_audio_length(audio_file)
        # if audio_length < self.min_audio_length:
        #     return {
        #         "success": False,
        #         "message": f"音频太短，至少需要{self.min_audio_length}秒"
        #     }

        # 生成音色名称
        if not voice_name:
            voice_name = f"voice_{len(list(self.voices_dir.glob('*'))):03d}"

        # 创建音色目录
        voice_dir = self.voices_dir / voice_name
        voice_dir.mkdir(exist_ok=True)

        # 复制音频文件到音色目录
        voice_audio_path = voice_dir / "reference.wav"
        shutil.copy(audio_file, voice_audio_path)

        # 这里应该调用RVC模型进行音色特征提取
        # 由于需要实际的模型，这里使用模拟实现
        features = self._extract_voice_features(audio_file)

        # 保存音色信息
        voice_info = {
            "name": voice_name,
            "audio_file": str(voice_audio_path),
            "features": features,
            "created_at": self._get_current_timestamp(),
            "status": "ready"
        }

        # 保存音色元数据
        self._save_voice_metadata(voice_dir, voice_info)

        logger.info(f"音色克隆完成 - 音色名称: {voice_name}")

        return {
            "success": True,
            "message": f"音色克隆成功！已保存为 '{voice_name}'",
            "voice_name": voice_name,
            "voice_path": str(voice_dir),
            "features": features
        }

    def _extract_voice_features(self, audio_file: str) -> Dict[str, Any]:
        """
        提取音色特征

        Args:
            audio_file: 音频文件路径

        Returns:
            音色特征字典
        """
        # 这里应该是实际的音色特征提取逻辑
        # 使用RVC模型或其他音色分析工具

        # 模拟实现
        features = {
            "gender": "unknown",  # male/female/unknown
            "pitch_range": "medium",
            "timbre": "neutral",
            "quality_score": 0.85
        }

        return features

    def _get_audio_length(self, audio_file: str) -> float:
        """
        获取音频长度

        Args:
            audio_file: 音频文件路径

        Returns:
            音频长度（秒）
        """
        # 这里应该使用librosa或soundfile获取实际长度
        import librosa
        y, sr = librosa.load(audio_file, sr=None)
        length = len(y) / sr
        return length

    def _save_voice_metadata(self, voice_dir: Path, metadata: Dict[str, Any]):
        """
        保存音色元数据

        Args:
            voice_dir: 音色目录
            metadata: 元数据字典
        """
        import json
        metadata_file = voice_dir / "metadata.json"

        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

    def _get_current_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()

    def list_voices(self) -> list:
        """
        列出所有可用的音色

        Returns:
            音色列表
        """
        voices = []

        for voice_dir in self.voices_dir.iterdir():
            if voice_dir.is_dir():
                metadata_file = voice_dir / "metadata.json"
                if metadata_file.exists():
                    import json
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    voices.append(metadata)

        return voices

    def get_voice_info(self, voice_name: str) -> Optional[Dict[str, Any]]:
        """
        获取音色信息

        Args:
            voice_name: 音色名称

        Returns:
            音色信息字典
        """
        voice_dir = self.voices_dir / voice_name
        metadata_file = voice_dir / "metadata.json"

        if not metadata_file.exists():
            return None

        import json
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        return metadata

    def delete_voice(self, voice_name: str) -> bool:
        """
        删除音色

        Args:
            voice_name: 音色名称

        Returns:
            是否删除成功
        """
        voice_dir = self.voices_dir / voice_name

        if not voice_dir.exists():
            return False

        shutil.rmtree(voice_dir)
        logger.info(f"音色已删除 - {voice_name}")

        return True

    def create_langchain_tool(self) -> Tool:
        """
        创建LangChain工具

        Returns:
            LangChain Tool对象
        """
        def clone_voice_wrapper(audio_file: str, voice_name: str = None) -> str:
            """包装函数，用于LangChain工具"""
            result = self.clone_voice(audio_file, voice_name)
            if result["success"]:
                return result["message"]
            else:
                return f"音色克隆失败: {result['message']}"

        def list_voices_wrapper() -> str:
            """列出所有音色的包装函数"""
            voices = self.list_voices()
            if not voices:
                return "当前没有可用的音色"

            voice_list = "\n".join([
                f"- {voice['name']}: {voice.get('status', 'unknown')}"
                for voice in voices
            ])
            return f"可用音色列表:\n{voice_list}"

        return Tool(
            name="音色克隆",
            func=clone_voice_wrapper,
            description=f"""
            从音频文件中提取音色特征并保存到音色仓库。
            音频文件应为{self.min_audio_length}-{self.max_audio_length}秒的清晰人声。
            参数:
            - audio_file: 音频文件路径（必需）
            - voice_name: 音色名称（可选，默认自动生成）
            """,
            return_direct=True
        )
