"""
任务规划模块
负责将复杂的用户请求分解为可执行的步骤
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import re
from loguru import logger


class TaskType(Enum):
    """任务类型枚举"""
    VOICE_CLONE = "voice_clone"
    VOICE_CONVERT = "voice_convert"
    PITCH_ADJUST = "pitch_adjust"
    TTS = "text_to_speech"
    AI_SINGING = "ai_singing"
    EMOTION_CONTROL = "emotion_control"
    BATCH_PROCESS = "batch_process"


@dataclass
class Task:
    """任务数据结构"""
    type: TaskType
    description: str
    parameters: Dict[str, Any]
    dependencies: List[str] = None
    priority: int = 5

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class TaskPlanner:
    """任务规划器"""

    def __init__(self):
        """初始化任务规划器"""
        self.task_templates = self._load_task_templates()
        logger.info("任务规划器初始化完成")

    def _load_task_templates(self) -> Dict[str, Dict]:
        """
        加载任务模板

        Returns:
            任务模板字典
        """
        return {
            "clone": {
                "keywords": ["克隆", "提取音色", "保存音色", "音色克隆"],
                "task_type": TaskType.VOICE_CLONE,
                "required_params": ["audio_file"],
                "optional_params": ["voice_name"]
            },
            "convert": {
                "keywords": ["转换", "替换音色", "音色转换", "变成"],
                "task_type": TaskType.VOICE_CONVERT,
                "required_params": ["target_audio", "source_voice"],
                "optional_params": ["pitch_shift"]
            },
            "pitch": {
                "keywords": ["升调", "降调", "音调", "调高", "调低"],
                "task_type": TaskType.PITCH_ADJUST,
                "required_params": ["audio_file"],
                "optional_params": ["semitones"]
            },
            "tts": {
                "keywords": ["朗读", "合成", "说话", "读出来"],
                "task_type": TaskType.TTS,
                "required_params": ["text"],
                "optional_params": ["voice", "emotion", "speed"]
            },
            "sing": {
                "keywords": ["唱", "歌曲", "唱歌", "演唱"],
                "task_type": TaskType.AI_SINGING,
                "required_params": ["lyrics"],
                "optional_params": ["voice", "style", "genre"]
            },
            "emotion": {
                "keywords": ["情感", "开心", "悲伤", "愤怒", "语气"],
                "task_type": TaskType.EMOTION_CONTROL,
                "required_params": ["audio_file"],
                "optional_params": ["emotion", "intensity"]
            }
        }

    def parse_user_request(self, user_input: str) -> List[Task]:
        """
        解析用户请求，生成任务列表

        Args:
            user_input: 用户输入文本

        Returns:
            任务列表
        """
        logger.info(f"解析用户请求: {user_input}")

        tasks = []
        user_input_lower = user_input.lower()

        # 检测任务类型
        detected_tasks = self._detect_task_types(user_input_lower)

        if not detected_tasks:
            # 如果没有检测到具体任务，创建一个通用咨询任务
            tasks.append(Task(
                type=TaskType.VOICE_CONVERT,
                description="用户咨询",
                parameters={"query": user_input},
                priority=10
            ))
            return tasks

        # 为每个检测到的任务创建Task对象
        for task_info in detected_tasks:
            task_type = task_info["type"]
            template = self._get_template_by_type(task_type)

            if template:
                # 提取参数
                parameters = self._extract_parameters(user_input, template)

                # 创建任务
                task = Task(
                    type=task_type,
                    description=task_info["description"],
                    parameters=parameters,
                    priority=task_info.get("priority", 5)
                )

                tasks.append(task)

                logger.info(f"创建任务 - 类型: {task_type}, 描述: {task_info['description']}")

        # 检查任务依赖关系
        tasks = self._resolve_dependencies(tasks)

        return tasks

    def _detect_task_types(self, user_input: str) -> List[Dict[str, Any]]:
        """
        检测用户输入中的任务类型

        Args:
            user_input: 用户输入

        Returns:
            检测到的任务类型列表
        """
        detected = []

        # 检查每种任务类型的关键词
        for task_name, template in self.task_templates.items():
            for keyword in template["keywords"]:
                if keyword in user_input:
                    detected.append({
                        "type": template["task_type"],
                        "description": f"{keyword}相关任务",
                        "priority": 5
                    })
                    break

        return detected

    def _get_template_by_type(self, task_type: TaskType) -> Optional[Dict]:
        """
        根据任务类型获取模板

        Args:
            task_type: 任务类型

        Returns:
            任务模板
        """
        for template in self.task_templates.values():
            if template["task_type"] == task_type:
                return template
        return None

    def _extract_parameters(self, user_input: str, template: Dict) -> Dict[str, Any]:
        """
        从用户输入中提取参数

        Args:
            user_input: 用户输入
            template: 任务模板

        Returns:
            提取的参数字典
        """
        parameters = {}

        # 提取数字（用于音调调节等）
        numbers = re.findall(r'-?\d+', user_input)
        if numbers:
            parameters["semitones"] = int(numbers[0])

        # 提取情感关键词
        emotion_keywords = {
            "开心": "happy",
            "悲伤": "sad",
            "愤怒": "angry",
            "平静": "neutral",
            "兴奋": "excited",
            "冷静": "calm"
        }

        for chinese, english in emotion_keywords.items():
            if chinese in user_input:
                parameters["emotion"] = english
                break

        # 提取文件路径（如果有）
        file_paths = re.findall(r'[\w\-\.]+\.(\w+)', user_input)
        if file_paths:
            parameters["audio_file"] = file_paths[0]

        return parameters

    def _resolve_dependencies(self, tasks: List[Task]) -> List[Task]:
        """
        解析任务依赖关系

        Args:
            tasks: 任务列表

        Returns:
            排序后的任务列表
        """
        # 简单的依赖关系解析
        # 如果需要音色转换，但还没有指定音色，可能需要先克隆音色

        for i, task in enumerate(tasks):
            if task.type == TaskType.VOICE_CONVERT:
                # 检查是否需要先克隆音色
                if "source_voice" not in task.parameters:
                    # 查找是否有克隆任务
                    clone_task = next(
                        (t for t in tasks if t.type == TaskType.VOICE_CLONE),
                        None
                    )
                    if clone_task:
                        task.dependencies.append("voice_clone")

        # 按优先级和依赖关系排序
        tasks.sort(key=lambda x: (len(x.dependencies), x.priority))

        return tasks

    def plan_execution_sequence(self, tasks: List[Task]) -> List[List[Task]]:
        """
        规划任务执行序列

        Args:
            tasks: 任务列表

        Returns:
            执行序列（可以并行的任务分组）
        """
        if not tasks:
            return []

        # 简单实现：每个任务单独执行
        # 更复杂的实现可以分析依赖关系，实现并行执行
        sequence = [[task] for task in tasks]

        logger.info(f"规划执行序列 - 共 {len(sequence)} 个步骤")
        return sequence

    def estimate_execution_time(self, tasks: List[Task]) -> int:
        """
        估算任务执行时间（秒）

        Args:
            tasks: 任务列表

        Returns:
            估算的执行时间
        """
        time_estimates = {
            TaskType.VOICE_CLONE: 30,
            TaskType.VOICE_CONVERT: 15,
            TaskType.PITCH_ADJUST: 5,
            TaskType.TTS: 10,
            TaskType.AI_SINGING: 60,
            TaskType.EMOTION_CONTROL: 10
        }

        total_time = sum(
            time_estimates.get(task.type, 10)
            for task in tasks
        )

        return total_time
