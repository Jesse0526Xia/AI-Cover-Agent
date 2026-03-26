"""
AI音频Agent主类
集成LangChain，提供智能音频处理能力
"""

import os
from typing import List, Dict, Any, Optional
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langchain import hub
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

from .memory import AgentMemory
from .planner import TaskPlanner, Task
from loguru import logger


class AudioAgent:
    """AI音频Agent核心类"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化AudioAgent

        Args:
            config: 配置字典
        """
        self.config = config

        # 初始化记忆管理器
        agent_config = config.get("agent", {})
        self.memory = AgentMemory(
            max_turns=agent_config.get("max_memory_turns", 10),
            enable_learning=agent_config.get("enable_learning", True)
        )

        # 初始化任务规划器
        self.planner = TaskPlanner()

        # 初始化LLM
        self.llm = self._init_llm()

        # 工具列表
        self.tools: List[Tool] = []

        # Agent执行器
        self.agent_executor: Optional[AgentExecutor] = None

        logger.info("AudioAgent初始化完成")

    def _init_llm(self) -> ChatOpenAI:
        """
        初始化语言模型

        Returns:
            ChatOpenAI实例
        """
        api_config = self.config.get("api", {}).get("openai", {})

        llm = ChatOpenAI(
            model=api_config.get("model", "gpt-4"),
            temperature=api_config.get("temperature", 0.7),
            max_tokens=api_config.get("max_tokens", 2000),
            api_key=api_config.get("api_key", os.getenv("OPENAI_API_KEY"))
        )

        logger.info(f"LLM初始化完成 - 模型: {api_config.get('model', 'gpt-4')}")

        return llm

    def register_tool(self, tool: Tool):
        """
        注册工具

        Args:
            tool: 工具对象
        """
        self.tools.append(tool)
        logger.info(f"注册工具 - {tool.name}")

    def build_agent(self):
        """构建Agent"""
        if not self.tools:
            logger.warning("没有注册任何工具，Agent将无法执行具体任务")

        # 获取Prompt模板
        try:
            prompt = hub.pull("hwchase17/openai-tools-agent")
        except Exception as e:
            logger.warning(f"无法从hub获取prompt模板: {e}")
            # 使用自定义prompt
            prompt = ChatPromptTemplate.from_messages([
                ("system", "你是一个专业的AI音频助手，能够处理音色克隆、转换、合成等任务。"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad")
            ])

        # 创建Agent
        agent = create_openai_tools_agent(self.llm, self.tools, prompt)

        # 创建执行器
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5,
            memory=self.memory
        )

        logger.info("Agent构建完成")

    async def chat(self, user_input: str) -> str:
        """
        与Agent对话

        Args:
            user_input: 用户输入

        Returns:
            Agent响应
        """
        # 添加用户消息到记忆
        self.memory.add_message("user", user_input)

        logger.info(f"用户输入: {user_input}")

        try:
            # 使用任务规划器分析请求
            tasks = self.planner.parse_user_request(user_input)

            if tasks and self.agent_executor:
                # 如果有具体任务，使用Agent执行
                response = await self.agent_executor.ainvoke({
                    "input": user_input
                })
                agent_response = response.get("output", "")
            else:
                # 如果没有具体任务或Agent未初始化，直接使用LLM
                messages = [
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": user_input}
                ]

                response = await self.llm.ainvoke(messages)
                agent_response = response.content

            # 添加Agent响应到记忆
            self.memory.add_message("assistant", agent_response)

            logger.info(f"Agent响应: {agent_response[:100]}...")

            return agent_response

        except Exception as e:
            logger.error(f"对话处理失败: {e}")
            error_response = f"抱歉，处理您的请求时出现了错误: {str(e)}"
            self.memory.add_message("assistant", error_response)
            return error_response

    def _get_system_prompt(self) -> str:
        """
        获取系统提示词

        Returns:
            系统提示词
        """
        agent_config = self.config.get("agent", {})
        personality = agent_config.get("personality", "专业的音频助手")

        prompt = f"""你是{personality}，名为AudioBot。

你的能力包括：
1. 音色克隆 - 从音频中提取音色特征
2. 音色转换 - 用指定音色替换音频中的音色
3. 音调调节 - 调整音频的音调（升调/降调）
4. 语音合成 - 用指定音色朗读文字
5. AI歌唱 - 用指定音色唱AI生成的歌曲
6. 情感控制 - 调整语音的情感表达

对话风格：
- 专业且友好
- 使用清晰的语言解释技术概念
- 适当使用音频相关的比喻
- 主动询问细节以确保准确理解需求

当前上下文：
{self.memory.get_context_summary()}
"""

        return prompt

    def process_task(self, task: Task) -> Dict[str, Any]:
        """
        处理单个任务

        Args:
            task: 任务对象

        Returns:
            处理结果
        """
        logger.info(f"处理任务 - 类型: {task.type}, 描述: {task.description}")

        # 这里会调用相应的工具来执行任务
        # 具体实现取决于注册的工具

        result = {
            "success": True,
            "task_type": task.type.value,
            "description": task.description,
            "message": "任务处理完成",
            "output": None
        }

        return result

    def get_available_tools(self) -> List[str]:
        """
        获取可用的工具列表

        Returns:
            工具名称列表
        """
        return [tool.name for tool in self.tools]

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """
        获取对话历史

        Returns:
            对话历史列表
        """
        return self.memory.get_conversation_history()

    def clear_memory(self):
        """清空记忆"""
        self.memory.clear_history()
        logger.info("Agent记忆已清空")

    def save_session(self, filepath: str):
        """
        保存会话

        Args:
            filepath: 保存路径
        """
        self.memory.save_to_file(filepath)

    def load_session(self, filepath: str):
        """
        加载会话

        Args:
            filepath: 加载路径
        """
        self.memory.load_from_file(filepath)

    def provide_feedback(self, feedback: Dict[str, Any]):
        """
        提供反馈

        Args:
            feedback: 反馈信息
        """
        self.memory.learn_from_feedback(feedback)
        logger.info("已接收用户反馈")
