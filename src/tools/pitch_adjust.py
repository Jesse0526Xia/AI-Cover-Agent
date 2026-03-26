"""
音调调节工具
调整音频的音调（升调/降调）
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path
from langchain.tools import Tool
from loguru import logger


class PitchAdjustTool:
    """音调调节工具"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化音调调节工具

        Args:
            config: 配置字典
        """
        self.config = config
        self.output_dir = Path(config.get("storage", {}).get("output_dir", "data/output/"))
        self.output_dir.mkdir(parents=True, exist_ok=True)

        tool_config = config.get("tools", {}).get("pitch_adjust", {})
        self.enabled = tool_config.get("enabled", True)
        self.min_semitones = tool_config.get("min_semitones", -12)
        self.max_semitones = tool_config.get("max_semitones", 12)

        # 常用预设
        self.presets = {
            "升八度": 12,
            "降八度": -12,
            "升五度": 7,
            "降五度": -7,
            "升四度": 5,
            "降四度": -5,
            "男声变女声": 4,
            "女声变男声": -4,
            "小黄人": 12,
            "低沉": -3,
            "高亢": 3
        }

        logger.info("音调调节工具初始化完成")

    def adjust_pitch(
        self,
        audio_file: str,
        semitones: int,
        output_file: Optional[str] = None,
        preserve_formants: bool = True
    ) -> Dict[str, Any]:
        """
        调整音调

        Args:
            audio_file: 音频文件路径
            semitones: 半音数（正数为升调，负数为降调）
            output_file: 输出文件路径（可选）
            preserve_formants: 是否保留共振峰（可选）

        Returns:
            调节结果
        """
        logger.info(f"开始音调调节 - 音频: {audio_file}, 半音: {semitones:+d}")

        # 验证音频文件
        if not os.path.exists(audio_file):
            return {
                "success": False,
                "message": f"音频文件不存在: {audio_file}"
            }

        # 验证半音范围
        if semitones < self.min_semitones or semitones > self.max_semitones:
            return {
                "success": False,
                "message": f"音调调整超出范围，允许范围: {self.min_semitones:+d} 到 {self.max_semitones:+d}"
            }

        # 生成输出文件名
        if not output_file:
            output_file = self._generate_output_filename(audio_file, semitones)

        # 执行音调调节
        try:
            adjusted_audio = self._perform_pitch_adjustment(
                audio_file,
                semitones,
                preserve_formants
            )

            # 保存调节后的音频
            output_path = self.output_dir / output_file
            self._save_audio(adjusted_audio, str(output_path))

            logger.info(f"音调调节完成 - 输出文件: {output_path}")

            return {
                "success": True,
                "message": f"音调调节成功！已{'升' if semitones > 0 else '降'}调{abs(semitones)}个半音，保存到 {output_file}",
                "output_file": str(output_path),
                "semitones": semitones,
                "duration": self._get_audio_duration(audio_file)
            }

        except Exception as e:
            logger.error(f"音调调节失败: {e}")
            return {
                "success": False,
                "message": f"音调调节失败: {str(e)}"
            }

    def _perform_pitch_adjustment(
        self,
        audio_file: str,
        semitones: int,
        preserve_formants: bool
    ) -> Any:
        """
        执行音调调节

        Args:
            audio_file: 音频文件
            semitones: 半音数
            preserve_formants: 是否保留共振峰

        Returns:
            调节后的音频数据
        """
        import librosa
        import soundfile as sf

        # 加载音频
        y, sr = librosa.load(audio_file, sr=None)

        # 执行音调变换
        y_shifted = librosa.effects.pitch_shift(
            y,
            sr=sr,
            n_steps=semitones,
            bins_per_octave=12
        )

        return y_shifted

    def _save_audio(self, audio_data: Any, output_path: str):
        """
        保存音频

        Args:
            audio_data: 音频数据
            output_path: 输出路径
        """
        import soundfile as sf
        sf.write(output_path, audio_data, 44100)

    def _generate_output_filename(self, audio_file: str, semitones: int) -> str:
        """
        生成输出文件名

        Args:
            audio_file: 输入音频文件
            semitones: 半音数

        Returns:
            输出文件名
        """
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prefix = os.path.splitext(os.path.basename(audio_file))[0]
        return f"{prefix}_pitch{semitones:+d}_{timestamp}.wav"

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

    def get_presets(self) -> Dict[str, int]:
        """
        获取可用的预设

        Returns:
            预设字典
        """
        return self.presets.copy()

    def apply_preset(
        self,
        audio_file: str,
        preset_name: str,
        output_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        应用预设

        Args:
            audio_file: 音频文件路径
            preset_name: 预设名称
            output_file: 输出文件路径（可选）

        Returns:
            调节结果
        """
        if preset_name not in self.presets:
            return {
                "success": False,
                "message": f"预设 '{preset_name}' 不存在。可用预设: {list(self.presets.keys())}"
            }

        semitones = self.presets[preset_name]
        return self.adjust_pitch(audio_file, semitones, output_file)

    def detect_pitch(self, audio_file: str) -> Dict[str, Any]:
        """
        检测音频的音高信息

        Args:
            audio_file: 音频文件路径

        Returns:
            音高信息
        """
        import librosa
        import numpy as np

        y, sr = librosa.load(audio_file, sr=None)

        # 提取音高
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)

        # 获取主要音高
        pitch_values = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            if pitch > 0:
                pitch_values.append(pitch)

        if not pitch_values:
            return {
                "success": False,
                "message": "无法检测到音高"
            }

        avg_pitch = np.mean(pitch_values)
        min_pitch = np.min(pitch_values)
        max_pitch = np.max(pitch_values)

        # 转换为音符
        def hz_to_note(hz):
            note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            note_num = 12 * (np.log2(hz / 440.0)) + 69
            note = note_names[int(note_num) % 12]
            octave = int(note_num / 12) - 1
            return f"{note}{octave}"

        return {
            "success": True,
            "avg_pitch_hz": float(avg_pitch),
            "min_pitch_hz": float(min_pitch),
            "max_pitch_hz": float(max_pitch),
            "avg_pitch_note": hz_to_note(avg_pitch),
            "pitch_range": f"{hz_to_note(min_pitch)} - {hz_to_note(max_pitch)}"
        }

    def create_langchain_tool(self) -> Tool:
        """
        创建LangChain工具

        Returns:
            LangChain Tool对象
        """
        def adjust_pitch_wrapper(
            audio_file: str,
            semitones: int
        ) -> str:
            """包装函数，用于LangChain工具"""
            result = self.adjust_pitch(audio_file, semitones)
            if result["success"]:
                return result["message"]
            else:
                return f"音调调节失败: {result['message']}"

        def apply_preset_wrapper(
            audio_file: str,
            preset_name: str
        ) -> str:
            """应用预设的包装函数"""
            result = self.apply_preset(audio_file, preset_name)
            if result["success"]:
                return result["message"]
            else:
                return f"应用预设失败: {result['message']}"

        def detect_pitch_wrapper(audio_file: str) -> str:
            """检测音高的包装函数"""
            result = self.detect_pitch(audio_file)
            if result["success"]:
                return f"""音高信息:
- 平均音高: {result['avg_pitch_note']} ({result['avg_pitch_hz']:.1f} Hz)
- 音高范围: {result['pitch_range']}"""
            else:
                return f"检测音高失败: {result['message']}"

        def list_presets_wrapper() -> str:
            """列出预设的包装函数"""
            presets = self.get_presets()
            preset_list = "\n".join([
                f"- {name}: {value:+d} 半音"
                for name, value in presets.items()
            ])
            return f"可用预设:\n{preset_list}"

        return Tool(
            name="音调调节",
            func=adjust_pitch_wrapper,
            description=f"""
            调整音频的音调（升调或降调）。

            参数:
            - audio_file: 音频文件路径（必需）
            - semitones: 半音数（必需，正数为升调，负数为降调）
              范围: {self.min_semitones:+d} 到 {self.max_semitones:+d}

            可用预设:
            {', '.join(self.presets.keys())}

            示例:
            - 升调3个半音
            - 降调2个半音
            - 使用"小黄人"预设
            """,
            return_direct=True
        )
