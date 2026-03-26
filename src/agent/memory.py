"""
Agent记忆管理模块
管理对话历史和用户偏好
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from loguru import logger


class AgentMemory:
    """Agent记忆管理器"""

    def __init__(self, max_turns: int = 10, enable_learning: bool = True):
        """
        初始化记忆管理器

        Args:
            max_turns: 最大记忆轮数
            enable_learning: 是否启用学习功能
        """
        self.max_turns = max_turns
        self.enable_learning = enable_learning
        self.conversation_history: List[Dict[str, Any]] = []
        self.user_preferences: Dict[str, Any] = {}
        self.session_id: str = datetime.now().strftime("%Y%m%d_%H%M%S")

        logger.info(f"Agent记忆管理器初始化完成 - Session: {self.session_id}")

    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """
        添加消息到对话历史

        Args:
            role: 消息角色 (user/assistant/system)
            content: 消息内容
            metadata: 额外的元数据
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }

        self.conversation_history.append(message)

        # 保持对话历史在限制范围内
        if len(self.conversation_history) > self.max_turns * 2:
            self.conversation_history = self.conversation_history[-self.max_turns * 2:]

        logger.debug(f"添加消息 - Role: {role}, Content长度: {len(content)}")

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """获取对话历史"""
        return self.conversation_history.copy()

    def get_recent_messages(self, n: int = 5) -> List[Dict[str, Any]]:
        """
       获取最近的n条消息

        Args:
            n: 消息数量

        Returns:
            最近的消息列表
        """
        return self.conversation_history[-n:] if self.conversation_history else []

    def clear_history(self):
        """清空对话历史"""
        self.conversation_history.clear()
        logger.info("对话历史已清空")

    def update_preference(self, key: str, value: Any):
        """
        更新用户偏好

        Args:
            key: 偏好键
            value: 偏好值
        """
        self.user_preferences[key] = value
        logger.info(f"更新用户偏好 - {key}: {value}")

    def get_preference(self, key: str, default: Any = None) -> Any:
        """
        获取用户偏好

        Args:
            key: 偏好键
            default: 默认值

        Returns:
            偏好值
        """
        return self.user_preferences.get(key, default)

    def learn_from_feedback(self, feedback: Dict[str, Any]):
        """
        从反馈中学习

        Args:
            feedback: 反馈信息
        """
        if not self.enable_learning:
            return

        # 提取偏好信息
        if "preferred_voice" in feedback:
            self.update_preference("preferred_voice", feedback["preferred_voice"])

        if "preferred_emotion" in feedback:
            self.update_preference("preferred_emotion", feedback["preferred_emotion"])

        if "preferred_pitch" in feedback:
            self.update_preference("preferred_pitch", feedback["preferred_pitch"])

        # 记录反馈
        feedback_record = {
            "timestamp": datetime.now().isoformat(),
            "feedback": feedback
        }

        if "feedback_history" not in self.user_preferences:
            self.user_preferences["feedback_history"] = []

        self.user_preferences["feedback_history"].append(feedback_record)

        logger.info(f"从反馈中学习 - 记录反馈: {feedback}")

    def get_context_summary(self) -> str:
        """
        获取上下文摘要

        Returns:
            对话上下文的摘要文本
        """
        if not self.conversation_history:
            return "当前没有对话历史"

        recent_messages = self.get_recent_messages(3)
        summary_parts = []

        for msg in recent_messages:
            role = "用户" if msg["role"] == "user" else "助手"
            content = msg["content"][:100]  # 限制长度
            summary_parts.append(f"{role}: {content}...")

        summary = "\n".join(summary_parts)

        # 添加用户偏好信息
        if self.user_preferences:
            pref_summary = "\n用户偏好: " + ", ".join(
                [f"{k}={v}" for k, v in self.user_preferences.items()
                 if k != "feedback_history"]
            )
            summary += pref_summary

        return summary

    def save_to_file(self, filepath: str):
        """
        保存记忆到文件

        Args:
            filepath: 文件路径
        """
        data = {
            "session_id": self.session_id,
            "conversation_history": self.conversation_history,
            "user_preferences": self.user_preferences,
            "saved_at": datetime.now().isoformat()
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"记忆已保存到文件: {filepath}")

    def load_from_file(self, filepath: str):
        """
        从文件加载记忆

        Args:
            filepath: 文件路径
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.session_id = data.get("session_id", self.session_id)
            self.conversation_history = data.get("conversation_history", [])
            self.user_preferences = data.get("user_preferences", {})

            logger.info(f"记忆已从文件加载: {filepath}")

        except Exception as e:
            logger.error(f"加载记忆文件失败: {e}")
