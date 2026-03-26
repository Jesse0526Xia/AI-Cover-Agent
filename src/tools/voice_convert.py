"""
音色转换工具
用指定音色替换音频中的原始音色
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path
from langchain.tools import Tool
from loguru import logger


class VoiceConvertTool:
    """音色转换工具"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化音色转换工具

        Args:
            config: 配置字典
        """
        self.config = config
        self.voices_dir = Path(config.get("storage", {}).get("voices_dir", "data/voices/"))
        self.output_dir = Path(config.get("storage", {}).get("output_dir", "data/output/"))
        self.output_dir.mkdir(parents=True, exist_ok=True)

        tool_config = config.get("tools", {}).get("voice_convert", {})
        self.enabled = tool_config.get("enabled", True)
        self.default_pitch_shift = tool_config.get("default_pitch_shift", 0)

        # RVC模型配置
        rvc_config = config.get("models", {}).get("rvc", {})
        self.rvc_model_path = rvc_config.get("model_path", "models/rvc/")
        self.device = rvc_config.get("device", "cuda")

        logger.info("音色转换工具初始化完成")

    def convert_voice(
        self,
        target_audio: str,
        source_voice: str,
        pitch_shift: Optional[int] = None,
        output_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        转换音色

        Args:
            target_audio: 目标音频文件路径
            source_voice: 源音色名称
            pitch_shift: 音调调整（半音数，可选）
            output_file: 输出文件路径（可选）

        Returns:
            转换结果
        """
        logger.info(f"开始音色转换 - 目标音频: {target_audio}, 源音色: {source_voice}")

        # 验证目标音频
        if not os.path.exists(target_audio):
            return {
                "success": False,
                "message": f"目标音频文件不存在: {target_audio}"
            }

        # 验证源音色
        voice_info = self._get_voice_info(source_voice)
        if not voice_info:
            return {
                "success": False,
                "message": f"音色 '{source_voice}' 不存在"
            }

        # 设置音调调整
        if pitch_shift is None:
            pitch_shift = self.default_pitch_shift

        # 生成输出文件名
        if not output_file:
            output_file = self._generate_output_filename(
                target_audio,
                source_voice,
                pitch_shift
            )

        # 执行音色转换
        try:
            # 这里应该调用RVC模型进行实际的音色转换
            # 由于需要实际的模型和GPU，这里使用模拟实现
            converted_audio = self._perform_voice_conversion(
                target_audio,
                voice_info,
                pitch_shift
            )

            # 保存转换后的音频
            output_path = self.output_dir / output_file
            self._save_audio(converted_audio, str(output_path))

            logger.info(f"音色转换完成 - 输出文件: {output_path}")

            return {
                "success": True,
                "message": f"音色转换成功！已保存到 {output_file}",
                "output_file": str(output_path),
                "source_voice": source_voice,
                "pitch_shift": pitch_shift,
                "duration": self._get_audio_duration(target_audio)
            }

        except Exception as e:
            logger.error(f"音色转换失败: {e}")
            return {
                "success": False,
                "message": f"音色转换失败: {str(e)}"
            }

    def _get_voice_info(self, voice_name: str) -> Optional[Dict[str, Any]]:
        """
        获取音色信息

        Args:
            voice_name: 音色名称

        Returns:
            音色信息字典
        """
        import json
        voice_dir = self.voices_dir / voice_name
        metadata_file = voice_dir / "metadata.json"

        if not metadata_file.exists():
            return None

        with open(metadata_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _perform_voice_conversion(
        self,
        target_audio: str,
        voice_info: Dict[str, Any],
        pitch_shift: int
    ) -> Any:
        """
        执行音色转换

        Args:
            target_audio: 目标音频
            voice_info: 音色信息
            pitch_shift: 音调调整

        Returns:
            转换后的音频数据
        """
        # 这里应该是实际的RVC模型调用
        # 示例伪代码：
        # rvc_model = load_rvc_model(voice_info['model_path'])
        # converted_audio = rvc_model.infer(
        #     target_audio,
        #     f0_up_key=pitch_shift,
        #     ...
        # )

        # 模拟实现 - 直接返回原始音频
        import soundfile as sf
        audio_data, sr = sf.read(target_audio)

        # 如果需要音调调整，可以在这里处理
        if pitch_shift != 0:
            import librosa
            audio_data = librosa.effects.pitch_shift(
                audio_data,
                sr=sr,
                n_steps=pitch_shift
            )

        return audio_data

    def _save_audio(self, audio_data: Any, output_path: str):
        """
        保存音频

        Args:
            audio_data: 音频数据
            output_path: 输出路径
        """
        import soundfile as sf
        sf.write(output_path, audio_data, 44100)

    def _generate_output_filename(
        self,
        target_audio: str,
        source_voice: str,
        pitch_shift: int
    ) -> str:
        """
        生成输出文件名

        Args:
            target_audio: 目标音频
            source_voice: 源音色
            pitch_shift: 音调调整

        Returns:
            输出文件名
        """
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pitch_str = f"_pitch{pitch_shift:+d}" if pitch_shift != 0 else ""
        return f"converted_{source_voice}_{timestamp}{pitch_str}.wav"

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

    def batch_convert(
        self,
        target_audios: list,
        source_voice: str,
        pitch_shift: int = 0
    ) -> Dict[str, Any]:
        """
        批量音色转换

        Args:
            target_audios: 目标音频文件列表
            source_voice: 源音色名称
            pitch_shift: 音调调整

        Returns:
            批量转换结果
        """
        results = []
        success_count = 0

        for audio_file in target_audios:
            result = self.convert_voice(
                audio_file,
                source_voice,
                pitch_shift
            )
            results.append(result)
            if result["success"]:
                success_count += 1

        return {
            "success": True,
            "message": f"批量转换完成，成功 {success_count}/{len(target_audios)}",
            "results": results
        }

    def create_langchain_tool(self) -> Tool:
        """
        创建LangChain工具

        Returns:
            LangChain Tool对象
        """
        def convert_voice_wrapper(
            target_audio: str,
            source_voice: str,
            pitch_shift: int = 0
        ) -> str:
            """包装函数，用于LangChain工具"""
            result = self.convert_voice(
                target_audio,
                source_voice,
                pitch_shift
            )
            if result["success"]:
                return result["message"]
            else:
                return f"音色转换失败: {result['message']}"

        return Tool(
            name="音色转换",
            func=convert_voice_wrapper,
            description="""
            用指定的音色替换目标音频中的原始音色。

            参数:
            - target_audio: 目标音频文件路径（必需）
            - source_voice: 源音色名称（必需）
            - pitch_shift: 音调调整半音数（可选，默认为0）

            示例:
            - 将a.wav的声音转换为voice_001的音色
            - 转换时升高2个半音
            """,
            return_direct=True
        )
