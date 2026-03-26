"""
情感控制工具
调整语音的情感表达
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path
from langchain.tools import Tool
from loguru import logger


class EmotionControlTool:
    """情感控制工具"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化情感控制工具

        Args:
            config: 配置字典
        """
        self.config = config
        self.output_dir = Path(config.get("storage", {}).get("output_dir", "data/output/"))
        self.output_dir.mkdir(parents=True, exist_ok=True)

        tool_config = config.get("tools", {}).get("emotion", {})
        self.enabled = tool_config.get("enabled", True)

        # 情感配置
        self.emotions = {
            "happy": {
                "description": "开心",
                "pitch_shift": 2,
                "speed": 1.1,
                "energy": 1.2,
                "characteristics": ["轻快", "明亮", "活泼"]
            },
            "sad": {
                "description": "悲伤",
                "pitch_shift": -2,
                "speed": 0.9,
                "energy": 0.8,
                "characteristics": ["低沉", "缓慢", "忧郁"]
            },
            "angry": {
                "description": "愤怒",
                "pitch_shift": 3,
                "speed": 1.2,
                "energy": 1.3,
                "characteristics": ["急促", "强烈", "尖锐"]
            },
            "neutral": {
                "description": "平静",
                "pitch_shift": 0,
                "speed": 1.0,
                "energy": 1.0,
                "characteristics": ["平稳", "自然", "清晰"]
            },
            "excited": {
                "description": "兴奋",
                "pitch_shift": 4,
                "speed": 1.3,
                "energy": 1.4,
                "characteristics": ["高亢", "快速", "热情"]
            },
            "calm": {
                "description": "冷静",
                "pitch_shift": -1,
                "speed": 0.95,
                "energy": 0.9,
                "characteristics": ["舒缓", "温和", "稳重"]
            },
            "surprised": {
                "description": "惊讶",
                "pitch_shift": 3,
                "speed": 1.1,
                "energy": 1.3,
                "characteristics": ["突然", "高昂", "鲜明"]
            },
            "fearful": {
                "description": "恐惧",
                "pitch_shift": -1,
                "speed": 1.0,
                "energy": 0.9,
                "characteristics": ["颤抖", "紧张", "压抑"]
            }
        }

        # 强度级别
        self.intensity_levels = {
            "low": 0.5,
            "medium": 1.0,
            "high": 1.5
        }

        logger.info("情感控制工具初始化完成")

    def control_emotion(
        self,
        audio_file: str,
        emotion: str,
        intensity: str = "medium",
        output_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        控制情感

        Args:
            audio_file: 音频文件路径
            emotion: 目标情感
            intensity: 强度（可选）
            output_file: 输出文件路径（可选）

        Returns:
            控制结果
        """
        logger.info(f"开始情感控制 - 音频: {audio_file}, 情感: {emotion}, 强度: {intensity}")

        # 验证音频文件
        if not os.path.exists(audio_file):
            return {
                "success": False,
                "message": f"音频文件不存在: {audio_file}"
            }

        # 验证情感
        if emotion not in self.emotions:
            return {
                "success": False,
                "message": f"不支持的情感 '{emotion}'。支持的情感: {', '.join(self.emotions.keys())}"
            }

        # 验证强度
        if intensity not in self.intensity_levels:
            return {
                "success": False,
                "message": f"不支持的强度 '{intensity}'。支持的强度: {', '.join(self.intensity_levels.keys())}"
            }

        # 生成输出文件名
        if not output_file:
            output_file = self._generate_output_filename(audio_file, emotion, intensity)

        # 执行情感控制
        try:
            controlled_audio = self._perform_emotion_control(
                audio_file,
                emotion,
                intensity
            )

            # 保存控制后的音频
            output_path = self.output_dir / output_file
            self._save_audio(controlled_audio, str(output_path))

            logger.info(f"情感控制完成 - 输出文件: {output_path}")

            emotion_config = self.emotions[emotion]

            return {
                "success": True,
                "message": f"情感控制成功！已应用{emotion_config['description']}情感（{intensity}强度），保存到 {output_file}",
                "output_file": str(output_path),
                "emotion": emotion,
                "emotion_description": emotion_config["description"],
                "intensity": intensity,
                "duration": self._get_audio_duration(audio_file),
                "characteristics": emotion_config["characteristics"]
            }

        except Exception as e:
            logger.error(f"情感控制失败: {e}")
            return {
                "success": False,
                "message": f"情感控制失败: {str(e)}"
            }

    def _perform_emotion_control(
        self,
        audio_file: str,
        emotion: str,
        intensity: str
    ) -> Any:
        """
        执行情感控制

        Args:
            audio_file: 音频文件
            emotion: 情感
            intensity: 强度

        Returns:
            控制后的音频数据
        """
        import librosa
        import numpy as np

        # 加载音频
        y, sr = librosa.load(audio_file, sr=None)

        # 获取情感配置
        emotion_config = self.emotions[emotion]
        intensity_factor = self.intensity_levels[intensity]

        # 应用音调调整
        pitch_shift = emotion_config["pitch_shift"] * intensity_factor
        if pitch_shift != 0:
            y = librosa.effects.pitch_shift(y, sr=sr, n_steps=pitch_shift)

        # 应用速度调整
        speed = emotion_config["speed"] * intensity_factor
        if speed != 1.0:
            y = librosa.effects.time_stretch(y, rate=speed)

        # 应用能量调整（音量）
        energy = emotion_config["energy"] * intensity_factor
        y = y * energy

        # 归一化
        y = y / np.max(np.abs(y)) * 0.8

        return y

    def _save_audio(self, audio_data: Any, output_path: str):
        """
        保存音频

        Args:
            audio_data: 音频数据
            output_path: 输出路径
        """
        import soundfile as sf
        sf.write(output_path, audio_data, 44100)

    def _generate_output_filename(self, audio_file: str, emotion: str, intensity: str) -> str:
        """
        生成输出文件名

        Args:
            audio_file: 输入音频文件
            emotion: 情感
            intensity: 强度

        Returns:
            输出文件名
        """
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prefix = os.path.splitext(os.path.basename(audio_file))[0]
        return f"{prefix}_{emotion}_{intensity}_{timestamp}.wav"

    def _get_audio_duration(self, audio_file: str) -> float:
        """
        获取音频时长

        Args:
            audio_file: 音频文件路径

        Returns:
            时长（秒）
        """
        import librosa
        y, sr = librosa.load(audio_file, sr=None)
        return len(y) / sr

    def get_supported_emotions(self) -> Dict[str, Dict[str, Any]]:
        """
        获取支持的情感列表

        Returns:
            情感字典
        """
        return {
            name: {
                "description": config["description"],
                "characteristics": config["characteristics"]
            }
            for name, config in self.emotions.items()
        }

    def get_intensity_levels(self) -> Dict[str, str]:
        """
        获取强度级别

        Returns:
            强度级别字典
        """
        return {
            "low": "低强度",
            "medium": "中强度",
            "high": "高强度"
        }

    def detect_emotion(self, audio_file: str) -> Dict[str, Any]:
        """
        检测音频中的情感（模拟实现）

        Args:
            audio_file: 音频文件路径

        Returns:
            检测到的情感信息
        """
        # 这里应该使用实际的情感识别模型
        # 简单实现：随机返回一个情感

        import random

        detected_emotion = random.choice(list(self.emotions.keys()))
        confidence = random.uniform(0.7, 0.95)

        emotion_config = self.emotions[detected_emotion]

        return {
            "success": True,
            "emotion": detected_emotion,
            "emotion_description": emotion_config["description"],
            "confidence": confidence,
            "characteristics": emotion_config["characteristics"],
            "message": f"检测到{emotion_config['description']}情感（置信度: {confidence:.1%}）"
        }

    def create_langchain_tool(self) -> Tool:
        """
        创建LangChain工具

        Returns:
            LangChain Tool对象
        """
        def control_emotion_wrapper(
            audio_file: str,
            emotion: str,
            intensity: str = "medium"
        ) -> str:
            """包装函数，用于LangChain工具"""
            result = self.control_emotion(audio_file, emotion, intensity)
            if result["success"]:
                return result["message"]
            else:
                return f"情感控制失败: {result['message']}"

        def detect_emotion_wrapper(audio_file: str) -> str:
            """检测情感的包装函数"""
            result = self.detect_emotion(audio_file)
            if result["success"]:
                return result["message"]
            else:
                return f"情感检测失败: {result['message']}"

        def list_emotions_wrapper() -> str:
            """列出情感的包装函数"""
            emotions = self.get_supported_emotions()
            emotion_list = "\n".join([
                f"- {name}: {info['description']} ({', '.join(info['characteristics'])})"
                for name, info in emotions.items()
            ])
            return f"支持的情感:\n{emotion_list}\n\n强度级别: {', '.join(self.get_intensity_levels().keys())}"

        return Tool(
            name="情感控制",
            func=control_emotion_wrapper,
            description=f"""
            调整音频的情感表达。

            参数:
            - audio_file: 音频文件路径（必需）
            - emotion: 目标情感（必需）
              支持的情感: {', '.join(self.emotions.keys())}
            - intensity: 强度（可选，默认为medium）
              支持的强度: {', '.join(self.intensity_levels.keys())}

            示例:
            - 将音频调整为开心情感
            - 用高强度应用悲伤情感
            - 检测音频中的情感
            """,
            return_direct=True
        )
