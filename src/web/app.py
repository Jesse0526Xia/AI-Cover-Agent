"""
AI音频Agent Web界面
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import sys
import yaml
from pathlib import Path
import asyncio
from loguru import logger

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


app = Flask(__name__)
CORS(app)

# 全局Agent实例
agent = None


def load_config(config_path: str = "config/config.yaml") -> dict:
    """加载配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        logger.info("配置文件加载成功")
        return config
    except Exception as e:
        logger.error(f"加载配置文件失败: {e}")
        return {}


def create_agent(config: dict) -> AudioAgent:
    """创建Agent实例"""
    logger.info("开始创建AI音频Agent...")

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

    agent.build_agent()

    logger.info("AI音频Agent创建完成")

    return agent


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    """聊天接口"""
    try:
        data = request.json
        user_input = data.get('message', '')

        if not user_input:
            return jsonify({'error': '消息不能为空'}), 400

        # 异步调用Agent
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(agent.chat(user_input))
        loop.close()

        return jsonify({
            'success': True,
            'response': response
        })

    except Exception as e:
        logger.error(f"聊天接口错误: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/tools', methods=['GET'])
def get_tools():
    """获取可用工具列表"""
    try:
        tools = agent.get_available_tools()
        return jsonify({
            'success': True,
            'tools': tools
        })
    except Exception as e:
        logger.error(f"获取工具列表错误: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/voices', methods=['GET'])
def get_voices():
    """获取音色列表"""
    try:
        # 这里需要实现获取音色列表的逻辑
        voices = []
        return jsonify({
            'success': True,
            'voices': voices
        })
    except Exception as e:
        logger.error(f"获取音色列表错误: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/clear', methods=['POST'])
def clear_memory():
    """清空对话历史"""
    try:
        agent.clear_memory()
        return jsonify({
            'success': True,
            'message': '对话历史已清空'
        })
    except Exception as e:
        logger.error(f"清空记忆错误: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/history', methods=['GET'])
def get_history():
    """获取对话历史"""
    try:
        history = agent.get_conversation_history()
        return jsonify({
            'success': True,
            'history': history
        })
    except Exception as e:
        logger.error(f"获取历史记录错误: {e}")
        return jsonify({'error': str(e)}), 500


def init_app():
    """初始化应用"""
    global agent

    # 设置日志
    logger.add(
        "logs/web.log",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        rotation="10 MB"
    )

    # 加载配置
    config = load_config()

    # 创建Agent
    agent = create_agent(config)

    logger.info("Web应用初始化完成")


if __name__ == '__main__':
    # 初始化应用
    init_app()

    # 启动服务器
    server_config = load_config().get("server", {})
    host = server_config.get("host", "0.0.0.0")
    port = server_config.get("port", 5000)

    logger.info(f"启动Web服务器: http://{host}:{port}")
    app.run(host=host, port=port, debug=True)
