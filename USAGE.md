# AI音频Agent 使用指南

## 快速开始

### 1. 环境准备

确保你的系统已安装：
- Python 3.8 或更高版本
- pip 包管理器
- CUDA 11.8+ (如果使用GPU加速)

### 2. 安装依赖

```bash
# 克隆或下载项目
cd demo

# 安装Python依赖
pip install -r requirements.txt
```

### 3. 配置设置

编辑 `config/config.yaml` 文件，设置你的API密钥：

```yaml
api:
  openai:
    api_key: "your-openai-api-key-here"  # 替换为你的OpenAI API密钥
```

### 4. 运行程序

#### 方式1: 命令行交互模式

```bash
python src/main.py
```

#### 方式2: Web界面模式

```bash
python src/web/app.py
```

然后在浏览器中打开: `http://localhost:5000`

## 功能使用

### 🎤 音色克隆

**命令示例：**
```
用户: 帮我克隆这个音频里的音色
用户: 克隆 audio.wav 的音色，命名为"温柔女声"
```

**参数说明：**
- audio_file: 音频文件路径
- voice_name: 音色名称（可选）

### 🔄 音色转换

**命令示例：**
```
用户: 用voice_001的音色转换这段音频
用户: 把target.wav转换为温柔女声的音色
用户: 用voice_001转换audio.wav，并升高2个半音
```

**参数说明：**
- target_audio: 目标音频文件
- source_voice: 源音色名称
- pitch_shift: 音调调整（可选）

### 🎵 音调调节

**命令示例：**
```
用户: 把这段音频升高3个半音
用户: 降低audio.wav的音调
用户: 使用"小黄人"预设
```

**参数说明：**
- audio_file: 音频文件
- semitones: 半音数（正数为升调，负数为降调）
- 预设: 升八度、降八度、男声变女声、小黄人等

### 🗣️ 语音合成

**命令示例：**
```
用户: 用开心的情感朗读"你好世界"
用户: 用voice_001朗读这首诗
用户: 用悲伤的情感说"今天天气不好"
```

**参数说明：**
- text: 要朗读的文本
- voice: 音色名称（可选）
- emotion: 情感（happy/sad/angry/neutral等）

### 🎶 AI歌唱

**命令示例：**
```
用户: 用流行风格唱"春天来了"
用户: 用voice_001唱一首关于爱情的歌曲
用户: 生成一首摇滚风格的歌
```

**参数说明：**
- lyrics: 歌词
- voice: 音色名称（可选）
- style: 音乐风格（pop/rock/ballad等）

### 🎭 情感控制

**命令示例：**
```
用户: 把这段音频调整为开心情感
用户: 用高强度应用悲伤情感
用户: 检测这段音频的情感
```

**参数说明：**
- audio_file: 音频文件
- emotion: 目标情感
- intensity: 强度（low/medium/high）

## 交互命令

在命令行模式中，可以使用以下命令：

- `help` - 显示帮助信息
- `clear` - 清空对话历史
- `tools` - 显示可用工具
- `voices` - 列出所有音色
- `exit` 或 `quit` - 退出程序

## 文件结构说明

```
demo/
├── config/              # 配置文件
│   ├── config.yaml      # 主配置
│   └── models.yaml      # 模型配置
├── data/                # 数据目录
│   ├── voices/          # 音色文件
│   ├── audio/           # 音频文件
│   └── output/          # 输出文件
├── src/                 # 源代码
│   ├── agent/           # Agent核心
│   ├── tools/           # 工具模块
│   ├── web/             # Web界面
│   └── main.py          # 主程序
└── requirements.txt     # 依赖列表
```

## 常见问题

### Q: 音色克隆需要多长的音频？

A: 建议使用5-60秒的清晰人声音频。音频越长，克隆效果越好。

### Q: 支持哪些音频格式？

A: 目前主要支持WAV格式，其他格式可以通过转换工具转换。

### Q: 如何提高音色转换的质量？

A:
1. 使用高质量的源音频
2. 确保目标音频清晰无杂音
3. 选择合适的音调调整值
4. 使用GPU加速处理

### Q: API密钥如何获取？

A: 需要注册OpenAI账号并获取API密钥：https://platform.openai.com/

### Q: 可以离线使用吗？

A: 部分功能需要联网（如LLM对话），但音频处理功能可以在本地运行。

## 技术支持

如有问题，请：
1. 查看日志文件：`logs/agent.log`
2. 检查配置文件是否正确
3. 确认所有依赖已正确安装

## 更新日志

### v1.0.0 (2024-03-26)
- ✨ 初始版本发布
- 🎤 音色克隆功能
- 🔄 音色转换功能
- 🎵 音调调节功能
- 🗣️ 语音合成功能
- 🎶 AI歌唱功能
- 🎭 情感控制功能
- 🤖 Agent智能对话
- 🌐 Web界面

## 许可证

MIT License

---

**让AI成为你的音频创作助手！** 🎵🤖
