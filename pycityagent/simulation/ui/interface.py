import tempfile
import time
from typing import TYPE_CHECKING, Any, Awaitable, Callable

import gradio as gr

from ..survey.models import QuestionType

if TYPE_CHECKING:
    from ..simulation import AgentSimulation


class InterviewUI:
    """模拟器界面"""

    def __init__(self, simulation: "AgentSimulation"):
        self.simulation = simulation
        self.interface = None

    def create_interface(self) -> gr.Blocks:
        """创建界面"""
        with gr.Blocks(title="智能体模拟器", theme=gr.themes.Ocean()) as interface:
            with gr.Tabs():
                # 采访标签页
                with gr.Tab("采访"):
                    self._create_interview_tab()

                # 问卷中心标签页
                with gr.Tab("问卷中心"):
                    self._create_survey_center_tab()

                # 问卷标签页
                with gr.Tab("问卷"):
                    self._create_survey_tab()

                # 状态标签页
                with gr.Tab("状态"):
                    self._create_status_tab()

            # 设置启动参数
            interface.launch_kwargs = {"quiet": True}  # type:ignore

            return interface

    def _create_interview_tab(self):
        """创建采访标签页"""
        # 上部：智能体选择和控制
        with gr.Group():
            with gr.Row():
                agent_dropdown = gr.Dropdown(
                    choices=self._get_agent_names(),
                    label="选择智能体",
                    interactive=True,
                )
                blocking_checkbox = gr.Checkbox(
                    label="阻塞控制", value=False, interactive=True
                )
                refresh_btn = gr.Button("刷新智能体列表")

            # 阻塞状态显示
            block_status = gr.Textbox(label="阻塞状态", value="", interactive=False)

        # 下部：对话区域
        with gr.Group():
            chatbot = gr.Chatbot(
                label="对话历史", type="messages", height=400  # 设置固定高度
            )

            with gr.Row():
                question = gr.Textbox(
                    label="提问", placeholder="请输入您的问题...", lines=2
                )
                send_btn = gr.Button("发送", variant="primary")

            with gr.Row():
                clear_btn = gr.Button("清空对话")
                export_btn = gr.Button("导出对话")

            # 导出对话文件组件
            export_file = gr.File(label="导出的对话记录", visible=True)

        # 事件处理
        refresh_btn.click(self._get_agent_names, outputs=agent_dropdown)

        def toggle_block(agent_name, blocking):
            if not agent_name:
                return "请先选择智能体"
            status = self.simulation.toggle_agent_block(agent_name, blocking)
            return status

        blocking_checkbox.change(
            toggle_block,
            inputs=[agent_dropdown, blocking_checkbox],
            outputs=[block_status],
        )

        def update_block_status(agent_name):
            if not agent_name:
                return False, ""
            is_blocked = agent_name in self.simulation._blocked_agents
            status = f"智能体 {agent_name} {'已阻塞' if is_blocked else '未阻塞'}"
            return is_blocked, status

        agent_dropdown.change(
            update_block_status,
            inputs=[agent_dropdown],
            outputs=[blocking_checkbox, block_status],
        )

        send_btn.click(
            self._handle_interview,
            inputs=[chatbot, agent_dropdown, question],
            outputs=[chatbot, question],
        )

        clear_btn.click(lambda: None, outputs=chatbot)

        def export_chat(agent_name):
            """导出对话历史"""
            if not agent_name:
                return None

            history = self.simulation.export_chat_history(agent_name)
            # 创建临时文件并写入内容
            with tempfile.NamedTemporaryFile(
                mode="w", delete=False, suffix=".json", encoding="utf-8"
            ) as f:
                f.write(history)
                return f.name

        export_btn.click(fn=export_chat, inputs=[agent_dropdown], outputs=[export_file])

    def _get_survey_table(self) -> list | None:
        """获取问卷列表数据"""
        surveys = self.simulation.get_surveys()
        if not surveys:
            return None
        return [[s.id, s.title, len(s.questions)] for s in surveys]

    def _get_survey_choices(self) -> list[str]:
        """获取问卷选择列表"""
        surveys = self.simulation.get_surveys()
        if not surveys:
            return []
        return [s.title for s in surveys]

    def _create_survey_center_tab(self):
        """创建问卷中心标签页"""
        # 状态控制
        survey_editor_visible = gr.Checkbox(value=False, visible=False)

        # 上部分：问卷列表展示
        gr.Markdown("### 问卷列表")
        with gr.Row():
            refresh_btn = gr.Button("刷新列表")
            new_survey_btn = gr.Button("新建问卷", variant="primary")

        # 问卷列表展示
        survey_table = gr.DataFrame(
            value=self._get_survey_table(),
            label="当前问卷列表",
            headers=["ID", "标题", "问题数量"],
            interactive=False,
        )

        # 问卷编辑区域
        with gr.Column(visible=False) as survey_editor:
            gr.Markdown("### 创建新问卷")
            # 基本信息
            survey_title = gr.Textbox(
                label="问卷标题", placeholder="请输入问卷标题...", interactive=True
            )
            survey_desc = gr.Textbox(
                label="问卷说明",
                lines=3,
                placeholder="请输入问卷说明...",
                interactive=True,
            )

            # 问题编辑
            with gr.Group():
                gr.Markdown("### 问题编辑")
                question_type = gr.Radio(
                    choices=[t.value for t in QuestionType],
                    label="问题类型",
                    value=QuestionType.TEXT.value,
                )
                question_content = gr.Textbox(
                    label="问题内容", lines=2, placeholder="请输入问题内容..."
                )

                # 选择题选项编辑
                with gr.Group(visible=False) as choice_editor:
                    gr.Markdown("#### 选项管理")
                    with gr.Row():
                        option_input = gr.Textbox(
                            label="选项内容", placeholder="请输入选项内容..."
                        )
                        add_option_btn = gr.Button("添加选项")
                    current_options = gr.Dataframe(
                        headers=["选项内容"], value=[], label="当前选项列表"
                    )
                    remove_option_btn = gr.Button("删除最后一个选项")

                # 评分题设置
                with gr.Group(visible=False) as rating_editor:
                    gr.Markdown("#### 评分设置")
                    with gr.Row():
                        min_score = gr.Number(label="最小分值", value=1, minimum=0)
                        max_score = gr.Number(label="最大分值", value=5, minimum=1)

                add_question_btn = gr.Button("添加问题", variant="primary")

            # 问题列表预览
            questions_preview = gr.Markdown("### 当前问题列表\n暂无问题")
            questions_data = gr.JSON(visible=False)  # 存储问题数据

            with gr.Row():
                save_survey_btn = gr.Button("保存问卷", variant="primary")
                clear_btn = gr.Button("清空")

        # 辅助函数
        def _get_survey_table(self) -> list | None:
            """获取问卷列表数据"""
            surveys = self.simulation._surveys
            if not surveys:
                return None
            return [[s["id"], s["title"], len(s["questions"])] for s in surveys]

        # 事件处理函数
        def refresh_table():
            """刷新问卷列表"""
            return self._get_survey_table()

        def toggle_editor(show):
            return {
                survey_editor: gr.update(visible=show),
                survey_title: gr.update(value=""),
                survey_desc: gr.update(value=""),
                # ... 其他需要重置的组件
            }

        # 绑定事件
        refresh_btn.click(fn=refresh_table, outputs=[survey_table])

        new_survey_btn.click(
            fn=lambda: toggle_editor(True),
            outputs=[
                survey_editor,
                survey_title,
                survey_desc,
                # ... 其他需要更新的组件
            ],
        )

        # 在事件绑定之前添加函数定义
        def update_question_editors(q_type):
            """更新问题编辑器的显示状态"""
            is_choice = q_type in [
                QuestionType.SINGLE_CHOICE.value,
                QuestionType.MULTIPLE_CHOICE.value,
            ]
            is_rating = q_type in [QuestionType.RATING.value, QuestionType.LIKERT.value]

            return {
                choice_editor: gr.update(visible=is_choice),
                rating_editor: gr.update(visible=is_rating),
                question_content: gr.update(),
                current_options: gr.update(value=[]),
                min_score: gr.update(value=1),
                max_score: gr.update(value=5),
            }

        # 然后是原有的事件绑定
        question_type.change(
            update_question_editors,
            inputs=[question_type],
            outputs=[
                choice_editor,
                rating_editor,
                question_content,
                current_options,
                min_score,
                max_score,
            ],
        )

        def add_option(option_text, current_options):
            """添加选项到列表"""
            if not option_text:
                return current_options, ""

            # 正确处理 DataFrame
            if current_options is None or current_options.empty:
                new_options = [[option_text]]
            else:
                new_options = current_options.values.tolist()
                # 添加新选项
                new_options.append([option_text])

            return new_options, ""

        add_option_btn.click(
            add_option,
            inputs=[option_input, current_options],
            outputs=[current_options, option_input],
        )

        # 在事件绑定之前添加函数定义
        def add_question(
            q_type, content, options, min_score, max_score, current_questions
        ):
            """添加问题到列表"""
            if not content:
                return current_questions, "### 当前问题列表\n请输入问题内容"

            questions = current_questions or []
            question = {"type": q_type, "content": content, "required": True}

            if q_type in [
                QuestionType.SINGLE_CHOICE.value,
                QuestionType.MULTIPLE_CHOICE.value,
            ]:
                # 正确处理 DataFrame 选项，并添加字母标号
                if options is not None and not options.empty:
                    raw_options = [opt[0] for opt in options.values.tolist()]
                    # 为选项添加字母标号 (a, b, c...)
                    question["options"] = [
                        f"{chr(97 + i)}. {opt}" for i, opt in enumerate(raw_options)
                    ]
                else:
                    question["options"] = []
            elif q_type in [QuestionType.RATING.value, QuestionType.LIKERT.value]:
                question["min_rating"] = min_score
                question["max_rating"] = max_score

            questions.append(question)

            # 更新预览，包含选项显示
            preview = "### 当前问题列表\n"
            for i, q in enumerate(questions, 1):
                preview += f"\n{i}. {q['content']}"
                if q.get("options"):
                    preview += "\n   " + "\n   ".join(q["options"])
                elif q.get("min_rating") is not None:
                    preview += f"\n   (评分范围: {q['min_rating']}-{q['max_rating']})"

            return questions, preview

        # 然后是事件绑定
        add_question_btn.click(
            add_question,
            inputs=[
                question_type,
                question_content,
                current_options,
                min_score,
                max_score,
                questions_data,
            ],
            outputs=[questions_data, questions_preview],
        )

        def save_survey(title, desc, questions):
            """保存问卷"""
            if not title:
                return [
                    False,  # survey_editor_visible
                    "",  # survey_title
                    "",  # survey_desc
                    "",  # question_content
                    [],  # current_options
                    None,  # questions_data
                    "### 当前问题列表\n暂无问题",  # questions_preview
                    None,  # survey_table
                    "请输入问卷标题",  # status message
                ]

            if not questions:
                return [
                    False,  # survey_editor_visible
                    "",  # survey_title
                    "",  # survey_desc
                    "",  # question_content
                    [],  # current_options
                    None,  # questions_data
                    "### 当前问题列表\n暂无问题",  # questions_preview
                    None,  # survey_table
                    "请添加至少一个问题",  # status message
                ]

            # 保存问卷并更新列表
            self.simulation.create_survey(
                title=title, description=desc, questions=questions
            )

            return [
                False,  # survey_editor_visible
                "",  # survey_title
                "",  # survey_desc
                "",  # question_content
                [],  # current_options
                None,  # questions_data
                "### 当前问题列表\n暂无问题",  # questions_preview
                self._get_survey_table(),  # survey_table
                "问卷保存成功",  # status message
            ]

        save_survey_btn.click(
            save_survey,
            inputs=[survey_title, survey_desc, questions_data],
            outputs=[
                survey_editor_visible,
                survey_title,
                survey_desc,
                question_content,
                current_options,
                questions_data,
                questions_preview,
                survey_table,  # 更新问卷列表
                gr.Markdown(),  # 状态消息
            ],
        )

        # 添加刷新按钮事件
        refresh_btn.click(
            lambda: self._get_survey_table(),
            outputs=[gr.Dropdown()],  # 更新所有问卷拉列表
        )

    def _create_survey_tab(self):
        """问卷标签页"""
        gr.Markdown("### 问卷提交")
        agent_select = gr.Dropdown(
            choices=self._get_agent_names(), label="选择智能体", interactive=True
        )
        survey_select = gr.Dropdown(
            choices=self._get_survey_choices() or [],  # 当��回None时使用���列表
            label="选择问卷",
            interactive=True,
            value=None,
        )
        refresh_btn = gr.Button("刷新列表")
        submit_btn = gr.Button("提交问卷", variant="primary")
        response_display = gr.Textbox(label="回答内容", lines=10, interactive=False)

        # 添加刷新事件处理
        def refresh_lists():
            return {
                agent_select: gr.Dropdown(
                    choices=self._get_agent_names(), interactive=True
                ),
                survey_select: gr.Dropdown(
                    choices=self._get_survey_choices() or [],
                    interactive=True,
                    value=None,
                ),
            }

        refresh_btn.click(refresh_lists, outputs=[agent_select, survey_select])

        # 绑定提交事件
        async def submit_survey(survey_title, agent_name):
            """提交问卷"""
            if not survey_title or not agent_name:
                return "请选择问卷和智能体"

            # 通过标题查找问卷ID
            surveys = self.simulation.get_surveys()
            survey_id = None
            survey = None
            for s in surveys:
                if s.title == survey_title:
                    survey_id = s.id
                    survey = s
                    break

            if not survey_id:
                return f"找不到指定的问卷, survey_title: {survey_title}, agent_name: {agent_name}"

            response = await self.simulation.submit_survey(agent_name, survey_id)
            return response

        submit_btn.click(
            submit_survey,
            inputs=[survey_select, agent_select],
            outputs=[response_display],
        )

    def _create_status_tab(self):
        """创建状态标签页"""
        with gr.Row():
            total_runtime = gr.Textbox(
                label="总运行时间",
                value=self.simulation.get_total_runtime(),
                interactive=False,
            )
            refresh_status_btn = gr.Button("刷新状态")

        # 添加全局阻塞控制
        with gr.Row():
            block_all_btn = gr.Button("阻塞所有智能体", variant="secondary")
            unblock_all_btn = gr.Button("解除所有阻塞", variant="secondary")

        with gr.Row():
            status_table = gr.DataFrame(
                self._get_agent_status(),
                label="智能体状态",
                headers=["名称", "类型", "状态", "运行时间", "操作"],
            )

        # 单个智能体阻塞控制
        with gr.Row():
            agent_select = gr.Dropdown(
                choices=self._get_agent_names(), label="选择智能体", interactive=True
            )
            block_status = gr.Textbox(label="阻塞状态", value="", interactive=False)
            toggle_block_btn = gr.Button("切换阻塞状态")

        self.status_table = status_table

        def update_status():
            total_time = self.simulation.get_total_runtime()
            status = self._get_agent_status()
            return total_time, status, self._get_agent_names()

        # 更新事件处理
        refresh_status_btn.click(
            update_status, outputs=[total_runtime, status_table, agent_select]
        )

        # 全局阻塞控制
        def block_all():
            for name in self.simulation._agents.keys():
                self.simulation.toggle_agent_block(name, True)
            return update_status()

        def unblock_all():
            for name in self.simulation._agents.keys():
                self.simulation.toggle_agent_block(name, False)
            return update_status()

        block_all_btn.click(
            block_all, outputs=[total_runtime, status_table, agent_select]
        )
        unblock_all_btn.click(
            unblock_all, outputs=[total_runtime, status_table, agent_select]
        )

        # 单个智能体阻塞控制
        def toggle_block(agent_name):
            if not agent_name:
                return "请先选择智能体", None, None, None
            is_blocked = agent_name in self.simulation._blocked_agents
            self.simulation.toggle_agent_block(agent_name, not is_blocked)
            status = f"智能体 {agent_name} {'已解除阻塞' if is_blocked else '已阻塞'}"
            return status, *update_status()

        toggle_block_btn.click(
            toggle_block,
            inputs=[agent_select],
            outputs=[block_status, total_runtime, status_table, agent_select],
        )

    def _get_agent_names(self) -> list[str]:
        """获取有智能体名称"""
        return list(self.simulation._agents.keys())

    def _get_agent_status(self) -> list[list]:
        """获取智能体状态信息"""
        status = []
        for name, agent in self.simulation._agents.items():
            status.append(
                [
                    name,
                    agent._type.value,
                    "暂停中" if name in self.simulation._blocked_agents else "运行中",
                    self.simulation.get_agent_runtime(name),
                ]
            )
        return status

    async def _handle_interview(self, history, agent_name, question):
        """处理采访请求"""
        if not agent_name:
            return (
                history + [{"role": "system", "content": "请先选择一个智能体"}],
                question,
            )

        if not question.strip():
            return history, question

        response = await self.simulation.interview_agent(agent_name, question)
        return (
            history
            + [
                {"role": "user", "content": question},
                {"role": "assistant", "content": response},
            ],
            "",
        )
