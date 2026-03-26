# AI音频Agent (AudioAgent)

一个智能的AI音频处理助手，能够理解自然语言指令，执行音色克隆、转换、合成等复杂音频任务。

## 核心功能

### 🎤 音色管理
- **音色克隆**: 从音频中提取音色特征并保存
- **音色仓库**: 管理多个音色，支持预览和编辑
- **音色转换**: 用指定音色替换音频中的原始音色

### 🎵 音调控制
- **音调调节**: 支持升调/降调（±12半音）
- **快速预设**: 性别转换、八度调节等
- **实时变换**: 播放时动态调整音调

### 🗣️ 语音合成
- **文字转语音**: 用指定音色朗读文本
- **情感控制**: 支持多种情感表达（开心、悲伤、愤怒等）
- **语调调节**: 控制语音的语调和节奏

### 🎶 AI歌唱
- **AI作曲**: 自动生成歌曲旋律
- **歌声合成**: 用指定音色演唱歌曲
- **歌词生成**: 根据主题生成歌词

### 🤖 Agent能力
- **自然语言理解**: 理解复杂的音频处理指令
- **智能任务规划**: 自动分解和执行任务
- **多轮对话**: 持续优化和调整结果
- **偏好学习**: 记住用户的常用设置

## 技术架构

```
AI音频Agent
├── 🧠 认知层 (LangChain Agent)
├── 🛠️ 执行层 (Audio Processing Tools)
├── 📚 知识库 (Voice Library & Templates)
└── 🎯 用户界面 (Web/Mobile/API)
```

## 快速开始

### 环境要求
- Python 3.8+
- CUDA 11.8+ (用于GPU加速)
- 8GB+ RAM

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置

1. 复制配置文件模板:
```bash
cp config/config.example.yaml config/config.yaml
```

2. 编辑配置文件，设置API密钥和模型路径

### 运行

```bash
# 启动Agent服务
python src/main.py

# 或者启动Web界面
python src/web/app.py
```

## 使用示例

### 对话示例

**音色克隆:**
```
用户: 帮我克隆这个音频里的音色
Agent: 好的，我来提取这个音频的音色特征...
```

**智能合成:**
```
用户: 用温柔女声，唱一首关于春天的歌，要开心一点的
Agent: 明白了！我将使用温柔女声音色，生成关于春天的欢快歌曲...
```

**音调调节:**
```
用户: 把这段录音的音调升高一点
Agent: 好的，我将音调升高2个半音...
```

## 项目结构

```
demo/
├── config/                 # 配置文件
│   ├── config.yaml         # 主配置
│   └── models.yaml         # 模型配置
├── src/
│   ├── agent/              # Agent核心
│   │   ├── __init__.py
│   │   ├── agent.py        # Agent主类
│   │   ├── memory.py       # 记忆管理
│   │   └── planner.py      # 任务规划
│   ├── tools/              # 工具模块
│   │   ├── __init__.py
│   │   ├── voice_clone.py  # 音色克隆
│   │   ├── voice_convert.py # 音色转换
│   │   ├── pitch_adjust.py # 音调调节
│   │   ├── tts.py          # 语音合成
│   │   ├── ai_singing.py   # AI歌唱
│   │   └── emotion.py      # 情感控制
│   ├── audio/              # 音频处理
│   │   ├── __init__.py
│   │   ├── processor.py    # 音频处理器
│   │   └── utils.py        # 音频工具
│   ├── models/             # 模型管理
│   │   ├── __init__.py
│   │   ├── rvc_manager.py  # RVC模型管理
│   │   └── model_loader.py # 模型加载器
│   ├── storage/            # 存储管理
│   │   ├── __init__.py
│   │   ├── voice_library.py # 音色仓库
│   │   └── file_manager.py # 文件管理
│   ├── web/                # Web界面
│   │   ├── app.py          # Flask应用
│   │   └── templates/      # HTML模板
│   └── main.py             # 主程序入口
├── tests/                  # 测试文件
├── data/                   # 数据目录
│   ├── voices/             # 音色文件
│   ├── audio/              # 音频文件
│   └── output/             # 输出文件
├── requirements.txt        # 依赖列表
└── README.md              # 项目说明
```

## 开发路线图

### Phase 1 - 基础框架 ✅
- [x] 项目结构搭建
- [x] Agent框架实现
- [x] 基础工具集成

### Phase 2 - 核心功能进行中
- [ ] 音色克隆工具
- [ ] 音色转换工具
- [ ] 音调调节工具

### Phase 3 - 高级功能
- [ ] 语音合成
- [ ] AI歌唱
- [ ] 情感控制

### Phase 4 - 智能优化
- [ ] 任务规划优化
- [ ] 质量评估
- [ ] 偏好学习

### Phase 5 - 产品化
- [ ] Web界面完善
- [ ] 性能优化
- [ ] 部署上线

## 技术栈

- **Agent框架**: LangChain
- **音频处理**: librosa, pydub, soundfile
- **音色转换**: RVC (Retrieval-based Voice Conversion)
- **语音合成**: GPT-SoVITS, Edge-TTS
- **音乐生成**: AudioLDM, MusicLM
- **Web框架**: Flask
- **数据库**: SQLite

## 贡献指南

欢迎提交Issue和Pull Request！

## 许可证

MIT License

## 联系方式

如有问题，请提交Issue或联系开发者。

---

**让AI成为你的音频创作助手！** 🎵🤖
