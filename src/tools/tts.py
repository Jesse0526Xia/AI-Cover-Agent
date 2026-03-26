"""
语音合成工具
用指定音色朗读文字，支持情感控制
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path
from langchain.tools import Tool
from loguru import logger


class TTSTool:
    """语音合成工具"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化语音合成工具

        Args:
            config: 配置字典
        """
        self.config = config
        self.output_dir = Path(config.get("storage", {}).get("output_dir", "data/output/"))
        self.output_dir.mkdir(parents=True, exist_ok=True)

        tool_config = config.get("tools", {}).get("tts", {})
        self.enabled = tool_config.get("enabled", True)
        self.supported_emotions = tool_config.get("supported_emotions", [
            "happy", "sad", "angry", "neutral", "excited", "calm"
        ])

        # 情感映射
        self.emotion_map = {
            "happy": {"description": "开心", "speed": 1.1, "pitch": 1.0},
            "sad": {"description": "悲伤", "speed": 0.9, "pitch": 0.9},
            "angry": {"description": "愤怒", "speed": 1.2, "pitch": 1.1},
            "neutral": {"description": "平静", "speed": 1.0, "pitch": 1.0},
            "excited": {"description": "兴奋", "speed": 1.2, "pitch": 1.1},
            "calm": {"description": "冷静", "speed": 0.9, "pitch": 0.95}
        }

        logger.info("语音合成工具初始化完成")

    def synthesize_speech(
        self,
        text: str,
        voice: Optional[str] = None,
        emotion: str = "neutral",
        speed: float = 1.0,
        output_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        合成语音

        Args:
            text: 要朗读的文本
            voice: 音色名称（可选）
            emotion: 情感（可选）
            speed: 语速（可选）
            output_file: 输出文件路径（可选）

        Returns:
            合成结果
        """
        logger.info(f"开始语音合成 - 文本: {text[:50]}..., 情感: {emotion}")

        # 验证情感
        if emotion not in self.supported_emotions:
            return {
                "success": False,
                "message": f"不支持的情感 '{emotion}'。支持的情感: {', '.join(self.supported_emotions)}"
            }

        # 生成输出文件名
        if not output_file:
            output_file = self._generate_output_filename(text, emotion)

        # 执行语音合成
        try:
            synthesized_audio = self._perform_synthesis(
                text,
                voice,
                emotion,
                speed
            )

            # 保存合成的音频
            output_path = self.output_dir / output_file
            self._save_audio(synthesized_audio, str(output_path))

            # 计算文本长度
            text_length = len(text)
            estimated_duration = self._estimate_duration(text, speed)

            logger.info(f"语音合成完成 - 输出文件: {output_path}")

            return {
                "success": True,
                "message": f"语音合成成功！已保存到 {output_file}",
                "output_file": str(output_path),
                "text": text,
                "voice": voice or "default",
                "emotion": emotion,
                "speed": speed,
                "text_length": text_length,
                "estimated_duration": estimated_duration
            }

        except Exception as e:
            logger.error(f"语音合成失败: {e}")
            return {
                "success": False,
                "message": f"语音合成失败: {str(e)}"
            }

    def _perform_synthesis(
        self,
        text: str,
        voice: Optional[str],
        emotion: str,
        speed: float
    ) -> Any:
        """
        执行语音合成

        Args:
            text: 文本
            voice: 音色
            emotion: 情感
            speed: 语速

        Returns:
            合成的音频数据
        """
        # 这里应该调用实际的TTS引擎
        # 可以使用Edge-TTS、GPT-SoVITS等

        # 模拟实现 - 生成简单的音频
        import numpy as np
        import soundfile as sf

        # 生成简单的正弦波音频（仅用于演示）
        duration = len(text) * 0.1 / speed  # 估算时长
        sample_rate = 22050
        t = np.linspace(0, duration, int(sample_rate * duration))

        # 根据情感调整频率
        emotion_config = self.emotion_map.get(emotion, self.emotion_map["neutral"])
        base_freq = 440 * emotion_config["pitch"]

        # 生成简单的音频波形
        audio = np.sin(2 * np.pi * base_freq * t)

        # 添加一些变化使其更自然
        audio += 0.3 * np.sin(2 * np.pi * base_freq * 1.5 * t)
        audio += 0.2 * np.sin(2 * np.pi * base_freq * 2 * t)

        # 归一化
        audio = audio / np.max(np.abs(audio)) * 0.8

        return audio

    def _save_audio(self, audio_data: Any, output_path: str):
        """
        保存音频

        Args:
            audio_data: 音频数据
            output_path: 输出路径
        """
        import soundfile as sf
        sf.write(output_path, audio_data, 22050)

    def _generate_output_filename(self, text: str, emotion: str) -> str:
        """
        生成输出文件名

        Args:
            text: 文本
            emotion: 情感

        Returns:
            输出文件名
        """
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        text_preview = text[:20].replace(" ", "_").replace("/", "_")
        return f"tts_{emotion}_{text_preview}_{timestamp}.wav"

    def _estimate_duration(self, text: str, speed: float) -> float:
        """
        估算音频时长

        Args:
            text: 文本
            speed: 语速

        Returns:
            时长（秒）
        """
        # 简单估算：每个字符约0.1秒
        base_duration = len(text) * 0.1
        return base_duration / speed

    def get_supported_emotions(self) -> Dict[str, str]:
        """
        获取支持的情感列表

        Returns:
            情感字典
        """
        return {
            emotion: config["description"]
            for emotion, config in self.emotion_map.items()
        }

    def batch_synthesize(
        self,
        texts: list,
        voice: Optional[str] = None,
        emotion: str = "neutral",
        speed: float = 1.0
    ) -> Dict[str, Any]:
        """
        批量语音合成

        Args:
            texts: 文本列表
            voice: 音色名称
            emotion: 情感
            speed: 语速

        Returns:
            批量合成结果
        """
        results = []
        success_count = 0

        for i, text in enumerate(texts):
            result = self.synthesize_speech(
                text,
                voice,
                emotion,
                speed
            )
            results.append({
                "index": i,
                "text": text[:50] + "..." if len(text) > 50 else text,
                **result
            })
            if result["success"]:
                success_count += 1

        return {
            "success": True,
            "message": f"批量合成完成，成功 {success_count}/{len(texts)}",
            "results": results
        }

    def create_langchain_tool(self) -> Tool:
        """
        创建LangChain工具

        Returns:
            LangChain Tool对象
        """
        def synthesize_speech_wrapper(
            text: str,
            voice: str = None,
            emotion: str = "neutral"
        ) -> str:
            """包装函数，用于LangChain工具"""
            result = self.synthesize_speech(text, voice, emotion)
            if result["success"]:
                return result["message"]
            else:
                return f"语音合成失败: {result['message']}"

        def list_emotions_wrapper() -> str:
            """列出情感的包装函数"""
            emotions = self.get_supported_emotions()
            emotion_list = "\n".join([
                f"- {name}: {desc}"
                for name, desc in emotions.items()
            ])
            return f"支持的情感:\n{emotion_list}"

        return Tool(
            name="语音合成",
            func=synthesize_speech_wrapper,
            description=f"""
            用指定的音色和情感朗读文字。

            参数:
            - text: 要朗读的文本（必需）
            - voice: 音色名称（可选）
            - emotion: 情感（可选，默认为neutral）
              支持的情感: {', '.join(self.supported_emotions)}

            示例:
            - 用开心情感朗读"你好世界"
            - 用悲伤情感朗读"今天天气不好"
            - 用指定音色朗读一首诗
            """,
            return_direct=True
        )
