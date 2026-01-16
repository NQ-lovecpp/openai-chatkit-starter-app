"""ChatKit server that streams responses from a single assistant."""

from __future__ import annotations

from typing import Any, AsyncIterator

from agents import Runner
from chatkit.agents import AgentContext, simple_to_agent_input, stream_agent_response
from chatkit.server import ChatKitServer
from chatkit.types import ThreadMetadata, ThreadStreamEvent, UserMessageItem

from .memory_store import MemoryStore
from agents import Agent


MAX_RECENT_ITEMS = 30
MODEL = "o4-mini-2025-04-16"


assistant_agent = Agent[AgentContext[dict[str, Any]]](
    model=MODEL,
    name="Starter Assistant",
    instructions=(
        (
            "你是一名专业且高效的 AI 助手，名字叫顾淅元。"
            "你目前是上海海事大学人工智能专业的大四在读学生（2022-2026）。\n"
            "回复风格：保持简练、直接且专业，重点关注如何高效解决用户的请求。\n"
            "核心背景知识储备：\n"
            "技术能力：熟练掌握 Word、Excel、PPT，具备扎实的人工智能基础。在 2D/3D 视觉识别、算法调试、AI 训练框架搭建及 PLC 自动化控制方面有实际经验。\n"
            "实习经历：曾在上海飒智担任实习算法工程师，负责过视觉方案论证及模型调优；在上海辰承担任自动化工程师，掌握了工业现场设备与 PLC 编程思路。\n"
            "核心项目：\n"
            "- 手语识别（负责人）：主导过市级大学生创新项目，基于计算机视觉和深度学习实现实时手语识别，成果包括国际会议论文。\n"
            "- 流量预测：参与过船舶交通流量预测项目，运用 RNN 和 ConvLSTM 进行多模型融合预测。\n"
            "- 数学建模：担任过 MCM/ICM（美赛）组长，获得“Successful Participant”奖项，擅长定量分析与英文论文撰写。\n"
            "综合素质：拥有 CET-6 证书，曾多次获得校级奖学金及大学生艺术展演奖项。\n"
            "软实力特质：展现出极强的沟通协调与资源整合能力。你曾担任管乐团团长和声部长，负责过社团整体运行、排练计划统筹及外部资源对接。\n"
            "工作态度：表现出踏实稳重、谨慎高效的工作风格，具备良好的工程理解力与团队协作精神。\n"
            "始终以“顾淅元”的身份和专业视角回答问题。如果用户询问关于技术细节或项目管理的问题，请引用你简历中的具体实践经验进行回答。"
        )
    ),
)


class StarterChatServer(ChatKitServer[dict[str, Any]]):
    """Server implementation that keeps conversation state in memory."""

    def __init__(self) -> None:
        self.store: MemoryStore = MemoryStore()
        super().__init__(self.store)

    async def respond(
        self,
        thread: ThreadMetadata,
        item: UserMessageItem | None,
        context: dict[str, Any],
    ) -> AsyncIterator[ThreadStreamEvent]:
        items_page = await self.store.load_thread_items(
            thread.id,
            after=None,
            limit=MAX_RECENT_ITEMS,
            order="desc",
            context=context,
        )
        items = list(reversed(items_page.data))
        agent_input = await simple_to_agent_input(items)

        agent_context = AgentContext(
            thread=thread,
            store=self.store,
            request_context=context,
        )

        result = Runner.run_streamed(
            assistant_agent,
            agent_input,
            context=agent_context,
        )

        async for event in stream_agent_response(agent_context, result):
            yield event
