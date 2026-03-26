"""
音频工具函数
"""

import os
from pathlib import Path
from typing import List, Optional
import librosa
import numpy as np
from loguru import logger


def validate_audio_file(file_path: str) -> bool:
    """
    验证音频文件

    Args:
        file_path: 文件路径

    Returns:
        是否有效
    """
    if not os.path.exists(file_path):
        logger.warning(f"文件不存在: {file_path}")
        return False

    valid_extensions = ['.wav', '.mp3', '.flac', '.ogg', '.m4a']
    ext = Path(file_path).suffix.lower()

    if ext not in valid_extensions:
        logger.warning(f"不支持的音频格式: {ext}")
        return False

    return True


def get_audio_info(file_path: str) -> dict:
    """
    获取音频信息

    Args:
        file_path: 文件路径

    Returns:
        音频信息字典
    """
    try:
        y, sr = librosa.load(file_path, sr=None, mono=True)
        duration = len(y) / sr

        info = {
            'file_path': file_path,
            'sample_rate': sr,
            'duration': duration,
            'channels': 1,  # librosa默认加载为单声道
            'format': Path(file_path).suffix[1:].upper()
        }

        return info

    except Exception as e:
        logger.error(f"获取音频信息失败: {e}")
        return {}


def batch_convert_format(
    input_files: List[str],
    output_dir: str,
    target_format: str = 'wav'
) -> List[str]:
    """
    批量转换音频格式

    Args:
        input_files: 输入文件列表
        output_dir: 输出目录
        target_format: 目标格式

    Returns:
        输出文件列表
    """
    import soundfile as sf

    output_files = []
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    for input_file in input_files:
        try:
            # 加载音频
            y, sr = librosa.load(input_file, sr=None, mono=True)

            # 生成输出文件名
            input_path = Path(input_file)
            output_file = Path(output_dir) / f"{input_path.stem}.{target_format}"

            # 保存
            sf.write(str(output_file), y, sr)
            output_files.append(str(output_file))

            logger.info(f"转换完成: {input_file} -> {output_file}")

        except Exception as e:
            logger.error(f"转换失败: {input_file}, 错误: {e}")

    return output_files


def mix_audio(files: List[str], output_file: str, weights: Optional[List[float]] = None):
    """
    混合多个音频文件

    Args:
        files: 音频文件列表
        output_file: 输出文件
        weights: 权重列表（可选）
    """
    if not files:
        raise ValueError("文件列表不能为空")

    if weights is None:
        weights = [1.0] * len(files)

    if len(files) != len(weights):
        raise ValueError("文件数量和权重数量不匹配")

    # 加载所有音频
    audios = []
    max_length = 0

    for file in files:
        y, sr = librosa.load(file, sr=None, mono=True)
        audios.append((y, sr))
        max_length = max(max_length, len(y))

    # 统一采样率
    target_sr = audios[0][1]

    # 混合
    mixed = np.zeros(max_length)

    for (y, sr), weight in zip(audios, weights):
        # 重采样
        if sr != target_sr:
            y = librosa.resample(y, orig_sr=sr, target_sr=target_sr)

        # 填充到相同长度
        if len(y) < max_length:
            y = np.pad(y, (0, max_length - len(y)))

        # 混合
        mixed += y * weight

    # 归一化
    mixed = mixed / np.max(np.abs(mixed)) * 0.8

    # 保存
    import soundfile as sf
    sf.write(output_file, mixed, target_sr)

    logger.info(f"音频混合完成: {output_file}")


def split_audio(
    file_path: str,
    output_dir: str,
    segment_duration: float = 30.0
) -> List[str]:
    """
    分割音频文件

    Args:
        file_path: 输入文件
        output_dir: 输出目录
        segment_duration: 每段时长（秒）

    Returns:
        输出文件列表
    """
    import soundfile as sf

    # 加载音频
    y, sr = librosa.load(file_path, sr=None, mono=True)
    total_duration = len(y) / sr

    # 计算段数
    num_segments = int(np.ceil(total_duration / segment_duration))

    output_files = []
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    for i in range(num_segments):
        start_sample = int(i * segment_duration * sr)
        end_sample = int((i + 1) * segment_duration * sr)
        segment = y[start_sample:end_sample]

        output_file = Path(output_dir) / f"{Path(file_path).stem}_part{i+1}.wav"
        sf.write(str(output_file), segment, sr)
        output_files.append(str(output_file))

        logger.info(f"分割完成: {output_file}")

    return output_files
