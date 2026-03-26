"""
音频处理器
提供基础的音频处理功能
"""

import numpy as np
import soundfile as sf
import librosa
from pathlib import Path
from typing import Tuple, Optional
from loguru import logger


class AudioProcessor:
    """音频处理器"""

    def __init__(self, sample_rate: int = 44100):
        """
        初始化音频处理器

        Args:
            sample_rate: 采样率
        """
        self.sample_rate = sample_rate
        logger.info(f"音频处理器初始化完成 - 采样率: {sample_rate}Hz")

    def load_audio(self, file_path: str) -> Tuple[np.ndarray, int]:
        """
        加载音频文件

        Args:
            file_path: 音频文件路径

        Returns:
            音频数据和采样率
        """
        try:
            audio, sr = librosa.load(file_path, sr=self.sample_rate, mono=True)
            logger.info(f"加载音频: {file_path}, 时长: {len(audio)/sr:.2f}秒")
            return audio, sr
        except Exception as e:
            logger.error(f"加载音频失败: {e}")
            raise

    def save_audio(self, audio: np.ndarray, file_path: str, sample_rate: Optional[int] = None):
        """
        保存音频文件

        Args:
            audio: 音频数据
            file_path: 保存路径
            sample_rate: 采样率（可选）
        """
        try:
            sr = sample_rate or self.sample_rate
            sf.write(file_path, audio, sr)
            logger.info(f"保存音频: {file_path}")
        except Exception as e:
            logger.error(f"保存音频失败: {e}")
            raise

    def normalize_audio(self, audio: np.ndarray, target_level: float = 0.8) -> np.ndarray:
        """
        归一化音频

        Args:
            audio: 音频数据
            target_level: 目标电平

        Returns:
            归一化后的音频
        """
        max_value = np.max(np.abs(audio))
        if max_value > 0:
            audio = audio / max_value * target_level
        return audio

    def trim_silence(self, audio: np.ndarray, threshold: float = 0.01) -> np.ndarray:
        """
        去除静音部分

        Args:
            audio: 音频数据
            threshold: 静音阈值

        Returns:
            去除静音后的音频
        """
        import librosa
        trimmed, _ = librosa.effects.trim(audio, top_db=20)
        return trimmed

    def get_duration(self, audio: np.ndarray) -> float:
        """
        获取音频时长

        Args:
            audio: 音频数据

        Returns:
            时长（秒）
        """
        return len(audio) / self.sample_rate

    def resample(self, audio: np.ndarray, target_sr: int) -> np.ndarray:
        """
        重采样

        Args:
            audio: 音频数据
            target_sr: 目标采样率

        Returns:
            重采样后的音频
        """
        import librosa
        return librosa.resample(audio, orig_sr=self.sample_rate, target_sr=target_sr)

    def apply_fade(self, audio: np.ndarray, fade_in: float = 0.1, fade_out: float = 0.1) -> np.ndarray:
        """
        应用淡入淡出

        Args:
            audio: 音频数据
            fade_in: 淡入时长（秒）
            fade_out: 淡出时长（秒）

        Returns:
            处理后的音频
        """
        fade_in_samples = int(fade_in * self.sample_rate)
        fade_out_samples = int(fade_out * self.sample_rate)

        result = audio.copy()

        # 淡入
        if fade_in_samples > 0:
            fade_in_curve = np.linspace(0, 1, fade_in_samples)
            result[:fade_in_samples] *= fade_in_curve

        # 淡出
        if fade_out_samples > 0:
            fade_out_curve = np.linspace(1, 0, fade_out_samples)
            result[-fade_out_samples:] *= fade_out_curve

        return result

    def detect_pitch(self, audio: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        检测音高

        Args:
            audio: 音频数据

        Returns:
            音高和强度
        """
        pitches, magnitudes = librosa.piptrack(y=audio, sr=self.sample_rate)
        return pitches, magnitudes
