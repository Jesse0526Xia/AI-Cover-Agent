"""
AI音频Agent主程序
"""

import asyncio
import sys
import yaml
from pathlib import Path
from loguru import logger

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent import AudioAgent
from src.tools import (
    VoiceCloneTool,
    VoiceConvertTool,
    PitchAdjustTool,
    TTSTool,
    AISingingTool,
    EmotionControlTool
)


def load_config(config_path: str = "config/config.yaml") -> dict:
    """
    加载配置文件

    Args:
        config_path: 配置文件路径

    Returns:
        配置字典
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        logger.info(f"配置文件加载成功: {config_path}")
        return config
    except Exception as e:
        logger.error(f"加载配置文件失败: {e}")
        # 返回默认配置
        return {}


def setup_logging(config: dict):
    """
    设置日志

    Args:
        config: 配置字典
    """
    log_config = config.get("logging", {})
    log_level = log_config.get("level", "INFO")
    log_file = log_config.get("file", "logs/agent.log")

    # 创建日志目录
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    # 配置日志
    logger.remove()
    logger.add(
        sys.stdout,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"
    )
    logger.add(
        log_file,
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        rotation="10 MB",
        retention="7 days"
    )

    logger.info("日志系统初始化完成")


def create_agent(config: dict) -> AudioAgent:
    """
    创建Agent实例

    Args:
        config: 配置字典

    Returns:
        AudioAgent实例
    """
    logger.info("开始创建AI音频Agent...")

    # 创建Agent
    agent = AudioAgent(config)

    # 注册工具
    tools_config = config.get("tools", {})

    if tools_config.get("voice_clone", {}).get("enabled", True):
        voice_clone_tool = VoiceCloneTool(config)
        agent.register_tool(voice_clone_tool.create_langchain_tool())
        logger.info("音色克隆工具已注册")

    if tools_config.get("voice_convert", {}).get("enabled", True):
        voice_convert_tool = VoiceConvertTool(config)
        agent.register_tool(voice_convert_tool.create_langchain_tool())
        logger.info("音色转换工具已注册")

    if tools_config.get("pitch_adjust", {}).get("enabled", True):
        pitch_adjust_tool = PitchAdjustTool(config)
        agent.register_tool(pitch_adjust_tool.create_langchain_tool())
        logger.info("音调调节工具已注册")

    if tools_config.get("tts", {}).get("enabled", True):
        tts_tool = TTSTool(config)
        agent.register_tool(tts_tool.create_langchain_tool())
        logger.info("语音合成工具已注册")

    if tools_config.get("ai_singing", {}).get("enabled", True):
        ai_singing_tool = AISingingTool(config)
        agent.register_tool(ai_singing_tool.create_langchain_tool())
        logger.info("AI歌唱工具已注册")

    if tools_config.get("emotion", {}).get("enabled", True):
        emotion_tool = EmotionControlTool(config)
        agent.register_tool(emotion_tool.create_langchain_tool())
        logger.info("情感控制工具已注册")

    # 构建Agent
    agent.build_agent()

    logger.info("AI音频Agent创建完成")

    return agent


def print_banner():
    """打印欢迎横幅"""
    banner = """
    ╔════════════════════════════════════════════════════════════╗
    ║                                                            ║
    ║           🎵 AI音频Agent (AudioBot) 🎵                     ║
    ║                                                            ║
    ║        智能音频处理助手 - 让音频创作更简单                  ║
    ║                                                            ║
    ║  功能:                                                     ║
    ║  🎤 音色克隆    🔄 音色转换    🎵 音调调节                  ║
    ║  🗣️ 语音合成    🎶 AI歌唱      🎭 情感控制                  ║
    ║                                                            ║
    ╚════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_help():
    """打印帮助信息"""
    help_text = """
    命令列表:
    ----------------------------------------------------------------
    交互命令:
      help                    - 显示帮助信息
      clear                   - 清空对话历史
      tools                   - 显示可用工具
      voices                  - 列出所有音色
      exit / quit             - 退出程序

    示例对话:
      - "帮我克隆这个音频里的音色"
      - "用voice_001的音色转换这段音频"
      - "把这段音频升高3个半音"
      - "用开心的情感朗读'你好世界'"
      - "用流行风格唱'春天来了'"
      - "检测这段音频的情感"

    ----------------------------------------------------------------
    """
    print(help_text)


async def interactive_mode(agent: AudioAgent):
    """
    交互模式

    Args:
        agent: Agent实例
    """
    print("\n🤖 AudioBot已就绪！输入你的需求，或输入'help'查看帮助。\n")

    while True:
        try:
            # 获取用户输入
            user_input = input("\n👤 你: ").strip()

            if not user_input:
                continue

            # 处理命令
            if user_input.lower() in ['exit', 'quit']:
                print("\n👋 再见！感谢使用AI音频Agent！")
                break

            elif user_input.lower() == 'help':
                print_help()
                continue

            elif user_input.lower() == 'clear':
                agent.clear_memory()
                print("🧹 对话历史已清空")
                continue

            elif user_input.lower() == 'tools':
                tools = agent.get_available_tools()
                print(f"\n🛠️ 可用工具 ({len(tools)}):")
                for tool in tools:
                    print(f"  - {tool}")
                continue

            elif user_input.lower() == 'voices':
                # 这里需要访问音色克隆工具
                print("\n🎤 音色列表功能需要先实现...")
                continue

            # 与Agent对话
            print("\n🤖 AudioBot: ", end="", flush=True)
            response = await agent.chat(user_input)
            print(response)

        except KeyboardInterrupt:
            print("\n\n👋 程序已中断。再见！")
            break
        except Exception as e:
            logger.error(f"处理用户输入时出错: {e}")
            print(f"\n❌ 出错了: {e}")


async def main():
    """主函数"""
    # 打印横幅
    print_banner()

    # 加载配置
    config = load_config()

    # 设置日志
    setup_logging(config)

    # 创建Agent
    try:
        agent = create_agent(config)

        # 启动交互模式
        await interactive_mode(agent)

    except Exception as e:
        logger.error(f"程序运行失败: {e}")
        print(f"\n❌ 程序启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # 运行主程序
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 程序已退出。")
        sys.exit(0)
