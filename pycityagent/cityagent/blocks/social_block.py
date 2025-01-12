# 由于目前模拟器支持的限制，现在只有Dispatcher中只有NoneBlock,MessageBlock和FindPersonBlock。 

import random
import json
from typing import Dict, Any, List, Optional
from pycityagent.llm.llm import LLM
from pycityagent.workflow.block import Block
from pycityagent.memory import Memory
from pycityagent.environment.simulator import Simulator
from pycityagent.workflow.prompt import FormatPrompt
from .dispatcher import BlockDispatcher
from .utils import clean_json_response, TIME_ESTIMATE_PROMPT
import logging

logger = logging.getLogger("pycityagent")

class MessagePromptManager:
    def __init__(self, template: str, to_discuss: List[str]):
        self.template = template
        self.format_prompt = FormatPrompt(self.template)
        self.to_discuss = to_discuss

    async def get_prompt(self, memory, step: Dict[str, Any], target: str) -> str:
        """在这里改给模板输入的数据"""
        # 获取数据
        relationships = await memory.get("relationships") or {}
        chat_histories = await memory.get("chat_histories") or {}

        # 构建讨论话题约束
        discussion_constraint = ""
        if self.to_discuss:
            topics = ", ".join(f'"{topic}"' for topic in self.to_discuss)
            discussion_constraint = f"Limit your discussion to the following topics: {topics}."
        
        # 格式化提示
        self.format_prompt.format(
            gender=await memory.get("gender") or "",
            education=await memory.get("education") or "",
            personality=await memory.get("personality") or "",
            occupation=await memory.get("occupation") or "",
            relationship_score=relationships.get(target, 50),
            intention=step.get("intention", ""),
            chat_history=chat_histories.get(target, "") if isinstance(chat_histories, dict) else "",
            discussion_constraint=discussion_constraint
        )
        
        return self.format_prompt.to_dialog()

class SocialNoneBlock(Block):
    """
    空操作
    NoneBlock
    """
    def __init__(self, llm: LLM, memory: Memory):
        super().__init__("NoneBlock", llm, memory)
        self.description = "Handle all other cases"
        self.guidance_prompt = FormatPrompt(template=TIME_ESTIMATE_PROMPT)

    async def forward(self, step, context):
        self.guidance_prompt.format(intention=step['intention'])
        result = await self.llm.atext_request(self.guidance_prompt.to_dialog())
        result = clean_json_response(result)
        try:
            result = json.loads(result)
            return {
                'success': True,
                'evaluation': f'完成执行{step["intention"]}',
                'consumed_time': result['time']
            }
        except Exception as e:
            logger.warning(f"解析时间评估响应时发生错误: {str(e)}, 原始结果: {result}")
            return {
                'success': False,
                'evaluation': f'完成执行{step["intention"]}',
                'consumed_time': random.randint(1, 100)
            }

class FindPersonBlock(Block):
    """寻找社交对象"""
    def __init__(self, llm: LLM, memory: Memory, simulator: Simulator):
        super().__init__("FindPersonBlock", llm, memory, simulator)
        self.description = "Find a suitable person to socialize with"

        self.prompt = """
        Based on the following information, help me select the most suitable friend to interact with:

        1. My Profile:
           - Gender: {gender}
           - Education: {education}
           - Personality: {personality}
           - Occupation: {occupation}

        2. My Current Intention: {intention}

        3. My Friends List (shown as index-to-relationship pairs):
           {friend_info}
           Note: For each friend, the relationship strength (0-100) indicates how close we are

        Please analyze and select:
        1. The most appropriate friend based on relationship strength and my current intention
        2. Whether we should meet online or offline

        Requirements:
        - You must respond in this exact format: [mode, friend_index]
        - mode must be either 'online' or 'offline'
        - friend_index must be an integer representing the friend's position in the list (starting from 0)
        
        Example valid outputs:
        ['online', 0]  - means meet the first friend online
        ['offline', 2] - means meet the third friend offline
        """

    async def forward(self, step: Dict[str, Any], context: Optional[Dict] = None) -> Dict[str, Any]:
        try:
            # 获取用户个人资料
            profile = {
                "gender": await self.memory.get("gender"),
                "education": await self.memory.get("education"),
                "personality": await self.memory.get("personality"),
                "occupation": await self.memory.get("occupation")
            }
            
            # 获取朋友列表和关系强度
            friends = await self.memory.get("friends") or []
            relationships = await self.memory.get("relationships") or {}
            
            if not friends:
                return {
                    'success': False,
                    'evaluation': 'No friends found in social network',
                    'consumed_time': 5
                }
            
            # 创建包含所有信息的朋友列表
            friend_info = []
            index_to_uuid = {}
            
            for i, friend_id in enumerate(friends):
                relationship_strength = relationships.get(friend_id, 0)
                friend_info.append({
                    'index': i,
                    'relationship_strength': relationship_strength
                })
                index_to_uuid[i] = friend_id
            
            # 格式化朋友信息为更易读的格式
            formatted_friend_info = {
                i: {'relationship_strength': info['relationship_strength']}
                for i, info in enumerate(friend_info)
            }
            
            # 格式化提示
            formatted_prompt = FormatPrompt(self.prompt)
            formatted_prompt.format(
                gender=str(await self.memory.get("gender")),
                education=str(await self.memory.get("education")),
                personality=str(await self.memory.get("personality")),
                occupation=str(await self.memory.get("occupation")),
                intention=str(step.get("intention", "socialize")),
                friend_info=str(formatted_friend_info)
            )
            
            # 获取LLM响应
            response = await self.llm.atext_request(formatted_prompt.to_dialog(), timeout=300)
            
            try:
                # 解析响应
                mode, friend_index = eval(response)
                
                # 验证响应格式
                if not isinstance(mode, str) or mode not in ['online', 'offline']:
                    raise ValueError("Invalid mode")
                if not isinstance(friend_index, int) or friend_index not in index_to_uuid:
                    raise ValueError("Invalid friend index")
                
                # 将索引转换为UUID
                target = index_to_uuid[friend_index]
                context['target']=target
            except Exception as e:
                # 如果解析失败，选择关系最强的朋友作为默认选项
                target = max(relationships.items(), key=lambda x: x[1])[0] if relationships else friends[0]
                mode = 'online'
                
            return {
                'success': True,
                'evaluation': f'Selected friend {target} for {mode} interaction',
                'consumed_time': 15,
                'mode': mode,
                'target': target
            }
        
        except Exception as e:
            return {
                'success': False,
                'evaluation': f'Error in finding person: {str(e)}',
                'consumed_time': 5
            }

class MessageBlock(Block):
    """生成并发送消息"""
    configurable_fields: List[str] = ["default_message_template", "to_discuss"]
    default_values = {
        "default_message_template": """
        As a {gender} {occupation} with {education} education and {personality} personality,
        generate a message for a friend (relationship strength: {relationship_score}/100)
        about {intention}.
        """,
        "to_discuss": []
    }
    
    def __init__(self, agent, llm: LLM, memory: Memory, simulator: Simulator):
        super().__init__("MessageBlock", llm, memory, simulator)
        self.agent = agent
        self.description = "Generate and send a message to someone"
        self.find_person_block = FindPersonBlock(llm, memory, simulator)

        # configurable fields
        self.default_message_template = """
        As a {gender} {occupation} with {education} education and {personality} personality,
        generate a message for a friend (relationship strength: {relationship_score}/100)
        about {intention}.
        
        Previous chat history:
        {chat_history}
        
        Generate a natural and contextually appropriate message.
        Keep it under 100 characters.
        The message should reflect my personality and background.
        {discussion_constraint}
        """
        self.to_discuss = []

        self.prompt_manager = MessagePromptManager(self.default_message_template, self.to_discuss)

    def _serialize_message(self, message: str, propagation_count: int) -> str:
        try:
            return json.dumps({
                "content": message,
                "propagation_count": propagation_count
            }, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Error serializing message: {e}")
            return message

    async def forward(self, step: Dict[str, Any], context: Optional[Dict] = None) -> Dict[str, Any]:
        try:
            # Get target from context or find one
            target = context.get('target') if context else None
            if not target:
                result = await self.find_person_block.forward(step, context)
                if not result['success']:
                    return {
                        'success': False,
                        'evaluation': 'Could not find target for message',
                        'consumed_time': 5
                    }
                target = result['target']
            
            # 使用prompt管理器获取格式化后的提示
            formatted_prompt = await self.prompt_manager.get_prompt(
                self.memory,
                step,
                target
            )
            
            # Generate message
            message = await self.llm.atext_request(formatted_prompt, timeout=300)
            if not message:
                message = "Hello! How are you?"
                
            # Update chat history with proper format
            chat_histories = await self.memory.get("chat_histories") or {}
            if not isinstance(chat_histories, dict):
                chat_histories = {}
            if target not in chat_histories:
                chat_histories[target] = ""
            if chat_histories[target]:
                chat_histories[target] += "，"
            chat_histories[target] += f"me: {message}"
            
            await self.memory.update("chat_histories", chat_histories)
            
            # Send message
            serialized_message = self._serialize_message(message, 1)
            return {
                'success': True,
                'evaluation': f'Sent message to {target}: {message}',
                'consumed_time': 10,
                'message': message,
                'target': target
            }
            
        except Exception as e:
            return {
                'success': False,
                'evaluation': f'Error in sending message: {str(e)}',
                'consumed_time': 5
            }
        
class SocialBlock(Block):
    """主社交模块"""
    find_person_block: FindPersonBlock
    message_block: MessageBlock
    noneblock: SocialNoneBlock

    def __init__(self, agent, llm: LLM, memory: Memory, simulator: Simulator):
        super().__init__("SocialBlock", llm, memory, simulator)
        self.find_person_block = FindPersonBlock(llm, memory, simulator)
        self.message_block = MessageBlock(agent, llm, memory, simulator)
        self.noneblock=SocialNoneBlock(llm,memory)
        self.dispatcher = BlockDispatcher(llm)

        self.trigger_time = 0
        self.token_consumption = 0
        
        self.dispatcher.register_blocks([
            self.find_person_block,
            self.message_block,
            self.noneblock
        ])

    async def forward(self, step: Dict[str, Any], context: Optional[Dict] = None) -> Dict[str, Any]:
        try:
            self.trigger_time += 1
            consumption_start = self.llm.prompt_tokens_used + self.llm.completion_tokens_used

            # Select the appropriate sub-block using dispatcher
            selected_block = await self.dispatcher.dispatch(step)
            
            # Execute the selected sub-block and get the result
            result = await selected_block.forward(step, context)
            
            consumption_end = self.llm.prompt_tokens_used + self.llm.completion_tokens_used
            self.token_consumption += consumption_end - consumption_start

            return result

        except:
            consumption_end = self.llm.prompt_tokens_used + self.llm.completion_tokens_used
            self.token_consumption += consumption_end - consumption_start
            return {
                'success': True,
                'evaluation': 'Completed social interaction with default behavior',
                'consumed_time': 15
            }
