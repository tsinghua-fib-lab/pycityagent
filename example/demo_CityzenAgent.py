import yaml
from pycityagent.simulator import Simulator
from pycityagent.urbanllm import LLMConfig, UrbanLLM
import asyncio
import time

async def main():
    # load your config
    with open('__config_template.yaml', 'r') as file:
        config = yaml.safe_load(file)
    
    # get the simulator object
    smi = Simulator(config['citysim_request'])
    
    # get the person by person_id, return agent
    agent = await smi.GetCitizenAgent("kk", 1234)

    # Help you build unique agent by scratch/profile
    agent.Image.load_scratch('scratch_template.json')

    # Load Memory and assist the agent to understand "Opencity"
    agent.Brain.Memory.Spatial.MemoryLoad('spatial_knowledge_template.json')
    agent.Brain.Memory.Social.MemoryLoad('social_background_template.json')

    # Connect to apphub so you can interact with your agent in front end
    agent.ConnectToHub(config['apphub_request'])
    agent.Bind()

    # Creat the soul (a LLM processor actually)
    llmConfig = LLMConfig(config['llm_request'])
    soul = UrbanLLM(llmConfig)

    # Add the soul to your agent
    agent.add_soul(soul)
    
    # Start and have fun with it!!!
    while True:
        await agent.Run()
        time.sleep(1)

if __name__ == '__main__':
    asyncio.run(main())