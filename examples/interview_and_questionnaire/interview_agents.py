import asyncio
import random
from typing import List, Dict
import yaml
from datetime import datetime

from pycityagent import CitizenAgent
from pycityagent.llm import LLM, LLMConfig, SimpleEmbedding
from pycityagent.memory import Memory
from pycityagent.simulation import AgentSimulation

# 定义一些常量
LOCATIONS = [
    {"id": "park_1", "name": "中央公园", "type": "park", "x": 100, "y": 100},
    {"id": "library_1", "name": "图书馆", "type": "library", "x": 200, "y": 150},
    {"id": "mall_1", "name": "购物中心", "type": "mall", "x": 300, "y": 200},
    {"id": "gym_1", "name": "体育馆", "type": "gym", "x": 400, "y": 250},
    {"id": "cafe_1", "name": "咖啡厅", "type": "cafe", "x": 500, "y": 300}
]

# 定义姓名列表
FIRST_NAMES = ["张", "王", "李", "赵", "刘", "陈", "杨", "黄", "周", "吴"]
LAST_NAMES = ["小", "大", "明", "华", "建", "文", "军", "国", "英", "志"]
LAST_NAMES_2 = ["伟", "强", "勇", "平", "安", "龙", "飞", "峰", "华", "明"]

class InterviewAgent(CitizenAgent):
    """可以接受采访的智能体"""
    
    async def forward(self) -> None:
        """智能体的行为逻辑：随机选择一个新地点"""
        current_location = await self.memory.get("location")
        # 从地点列表中随机选择一个新地点（排除当前地点）
        available_locations = [loc for loc in LOCATIONS if loc["id"] != current_location["id"]]
        new_location = random.choice(available_locations)
        print(f"智能体 {self._name} 移动到 {new_location['name']}")
        
        # 更新位置
        await self.memory.update("location", new_location)
        await self.memory.update("x", new_location["x"])
        await self.memory.update("y", new_location["y"])
        await asyncio.sleep(random.uniform(1, 3))

async def main():
    """主函数"""
    # 加载配置
    with open("__config_template.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    # 初始化LLM
    llm_config = LLMConfig(config["llm_request"])
    llm = LLM(llm_config)
    
    # 初始化Embedding模型
    embedding_model = SimpleEmbedding(vector_dim=128, cache_size=1000)
    
    # 创建模拟器
    simulation = AgentSimulation()
    
    # 创建并添加智能体
    for i in range(10):
        # 随机生成真实姓名
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES) + random.choice(LAST_NAMES_2)
        name = first_name + last_name
        
        # 随机选择初始位置
        initial_location = random.choice(LOCATIONS)
        
        # 配置记忆
        memory_config = {
            "name": (str, name, True),
            "location": (dict, initial_location, True),
            "x": (float, initial_location["x"], False),
            "y": (float, initial_location["y"], False),
            "visited_locations": (list, [], True),
        }
        
        # 创建Memory实例
        memory = Memory(
            config=memory_config,
            embedding_model=embedding_model
        )
        
        # 创建智能体
        agent = InterviewAgent(
            name=name,
            llm_client=llm,
            memory=memory
        )
        
        # 添加到模拟器
        simulation.add_agent(agent)
    
    # 运行模拟器（会自动启动UI）
    await simulation.run(interval=3)

if __name__ == "__main__":
    asyncio.run(main()) 