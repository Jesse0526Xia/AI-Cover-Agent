"""
AI歌唱工具
用指定音色唱AI生成的歌曲
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path
from langchain.tools import Tool
from loguru import logger


class AISingingTool:
    """AI歌唱工具"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化AI歌唱工具

        Args:
            config: 配置字典
        """
        self.config = config
        self.output_dir = Path(config.get("storage", {}).get("output_dir", "data/output/"))
        self.output_dir.mkdir(parents=True, exist_ok=True)

        tool_config = config.get("tools", {}).get("ai_singing", {})
        self.enabled = tool_config.get("enabled", True)
        self.max_duration = tool_config.get("max_duration", 180)  # 秒

        # 音乐风格配置
        self.music_styles = {
            "pop": {"description": "流行音乐", "tempo": 120, "energy": "medium"},
            "rock": {"description": "摇滚", "tempo": 140, "energy": "high"},
            "ballad": {"description": "民谣", "tempo": 80, "energy": "low"},
            "electronic": {"description": "电子音乐", "tempo": 128, "energy": "high"},
            "jazz": {"description": "爵士", "tempo": 100, "energy": "medium"},
            "classical": {"description": "古典", "tempo": 90, "energy": "low"}
        }

        logger.info("AI歌唱工具初始化完成")

    def generate_singing(
        self,
        lyrics: str,
        voice: Optional[str] = None,
        style: str = "pop",
        genre: str = "pop",
        melody: Optional[str] = None,
        output_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        生成AI歌声

        Args:
            lyrics: 歌词
            voice: 音色名称（可选）
            style: 风格（可选）
            genre: 音乐类型（可选）
            melody: 旋律描述（可选）
            output_file: 输出文件路径（可选）

        Returns:
            生成结果
        """
        logger.info(f"开始生成AI歌声 - 歌词: {lyrics[:50]}..., 风格: {style}")

        # 验证风格
        if style not in self.music_styles:
            return {
                "success": False,
                "message": f"不支持的风格 '{style}'。支持的风格: {', '.join(self.music_styles.keys())}"
            }

        # 生成输出文件名
        if not output_file:
            output_file = self._generate_output_filename(lyrics, style)

        # 执行歌声生成
        try:
            singing_audio = self._perform_singing_generation(
                lyrics,
                voice,
                style,
                genre,
                melody
            )

            # 保存生成的音频
            output_path = self.output_dir / output_file
            self._save_audio(singing_audio, str(output_path))

            # 估算时长
            duration = self._estimate_duration(lyrics, style)

            logger.info(f"AI歌声生成完成 - 输出文件: {output_path}")

            return {
                "success": True,
                "message": f"AI歌声生成成功！已保存到 {output_file}",
                "output_file": str(output_path),
                "lyrics": lyrics,
                "voice": voice or "default",
                "style": style,
                "genre": genre,
                "duration": duration,
                "melody": melody or "auto-generated"
            }

        except Exception as e:
            logger.error(f"AI歌声生成失败: {e}")
            return {
                "success": False,
                "message": f"AI歌声生成失败: {str(e)}"
            }

    def _perform_singing_generation(
        self,
        lyrics: str,
        voice: Optional[str],
        style: str,
        genre: str,
        melody: Optional[str]
    ) -> Any:
        """
        执行歌声生成

        Args:
            lyrics: 歌词
            voice: 音色
            style: 风格
            genre: 类型
            melody: 旋律

        Returns:
            生成的音频数据
        """
        # 这里应该调用实际的AI歌声生成模型
        # 可以使用So-VITS-SVC、Fish-SVC等

        # 模拟实现 - 生成简单的音频
        import numpy as np
        import soundfile as sf

        # 根据风格设置参数
        style_config = self.music_styles.get(style, self.music_styles["pop"])
        tempo = style_config["tempo"]

        # 估算时长
        duration = self._estimate_duration(lyrics, style)
        sample_rate = 22050
        t = np.linspace(0, duration, int(sample_rate * duration))

        # 生成简单的音频波形（模拟歌声）
        audio = np.zeros_like(t)

        # 为每个音节生成音频
        syllables = len(lyrics.split())
        syllable_duration = duration / max(syllables, 1)

        for i in range(syllables):
            start_idx = int(i * syllable_duration * sample_rate)
            end_idx = int((i + 1) * syllable_duration * sample_rate)

            # 生成音高变化（模拟旋律）
            freq = 220 + (i % 8) * 50  # 简单的音高变化
            syllable_t = np.linspace(0, syllable_duration, end_idx - start_idx)

            # 生成波形
            waveform = np.sin(2 * np.pi * freq * syllable_t)
            waveform += 0.3 * np.sin(2 * np.pi * freq * 2 * syllable_t)

            # 添加到音频
            audio[start_idx:end_idx] = waveform

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

    def _generate_output_filename(self, lyrics: str, style: str) -> str:
        """
        生成输出文件名

        Args:
            lyrics: 歌词
            style: 风格

        Returns:
            输出文件名
        """
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        lyrics_preview = lyrics[:20].replace(" ", "_").replace("/", "_")
        return f"singing_{style}_{lyrics_preview}_{timestamp}.wav"

    def _estimate_duration(self, lyrics: str, style: str) -> float:
        """
        估算音频时长

        Args:
            lyrics: 歌词
            style: 风格

        Returns:
            时长（秒）
        """
        # 根据歌词长度和风格估算
        style_config = self.music_styles.get(style, self.music_styles["pop"])
        tempo = style_config["tempo"]

        # 简单估算：每个音节约0.5秒
        syllables = len(lyrics.split())
        base_duration = syllables * 0.5

        # 根据速度调整
        speed_factor = 120 / tempo
        duration = base_duration * speed_factor

        # 限制最大时长
        return min(duration, self.max_duration)

    def generate_lyrics(self, topic: str, style: str = "pop") -> str:
        """
        生成歌词

        Args:
            topic: 主题
            style: 风格

        Returns:
            生成的歌词
        """
        # 这里应该调用LLM生成歌词
        # 简单实现：返回示例歌词

        lyrics_templates = {
            "pop": f"""
{topic} - 流行风格

(主歌)
在这个{topic}的世界里
我寻找着属于自己的意义
每一个瞬间都值得珍惜
让我们一起创造奇迹

(副歌)
哦~ {topic}
你是我的梦想
哦~ {topic}
带我飞翔

(桥段)
无论风雨无论困难
我们都不会放弃
因为有你在我身边
一切都变得有意义
""",
            "ballad": f"""
{topic} - 民谣风格

(主歌1)
静静思考{topic}的意义
时光流逝如水般清晰
回忆中的点点滴滴
都是生命中最美的印记

(主歌2)
走过春夏秋冬的轮回
感受{topic}带来的安慰
在月光下轻声低语
诉说心中最深情的秘密

(副歌)
{topic}啊~ {topic}
你是我心中永恒的歌谣
{topic}啊~ {topic}
带我穿越岁月的浪潮
""",
            "rock": f"""
{topic} - 摇滚风格

(主歌)
{topic}！
燃烧吧！
打破所有的束缚
释放内心的力量

(副歌)
{topic}！
冲破黑暗！
让世界听到我们的声音
{topic}！
永不放弃！

(桥段)
即使前路充满荆棘
我们也要勇往直前
因为{topic}就在前方
等待我们去征服
"""
        }

        return lyrics_templates.get(style, lyrics_templates["pop"])

    def get_music_styles(self) -> Dict[str, str]:
        """
        获取支持的音乐风格

        Returns:
            风格字典
        """
        return {
            style: config["description"]
            for style, config in self.music_styles.items()
        }

    def create_langchain_tool(self) -> Tool:
        """
        创建LangChain工具

        Returns:
            LangChain Tool对象
        """
        def generate_singing_wrapper(
            lyrics: str,
            voice: str = None,
            style: str = "pop"
        ) -> str:
            """包装函数，用于LangChain工具"""
            result = self.generate_singing(lyrics, voice, style)
            if result["success"]:
                return result["message"]
            else:
                return f"AI歌声生成失败: {result['message']}"

        def generate_lyrics_wrapper(topic: str, style: str = "pop") -> str:
            """生成歌词的包装函数"""
            lyrics = self.generate_lyrics(topic, style)
            return f"生成的歌词:\n{lyrics}"

        def list_styles_wrapper() -> str:
            """列出风格的包装函数"""
            styles = self.get_music_styles()
            style_list = "\n".join([
                f"- {name}: {desc}"
                for name, desc in styles.items()
            ])
            return f"支持的音乐风格:\n{style_list}"

        return Tool(
            name="AI歌唱",
            func=generate_singing_wrapper,
            description=f"""
            用指定音色唱AI生成的歌曲。

            参数:
            - lyrics: 歌词（必需）
            - voice: 音色名称（可选）
            - style: 音乐风格（可选，默认为pop）
              支持的风格: {', '.join(self.music_styles.keys())}

            示例:
            - 用流行风格唱"春天来了"
            - 用民谣风格唱一首关于爱情的歌曲
            - 用摇滚风格唱"自由飞翔"
            """,
            return_direct=True
        )
