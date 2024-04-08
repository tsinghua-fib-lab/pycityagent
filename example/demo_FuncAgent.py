import yaml
import pycityagent
from pycityagent.urbanllm import LLMConfig, UrbanLLM
import asyncio
import time
from pycityagent.brain.memory import LTMemory
from pycityagent.brain.memory import MemoryRetrive
from pycityagent.brain.memory import MemoryReason
from pycityagent.brain.memory import MemoryPersistence
from pycityagent.cc import Command
from pycityagent.ac.action import *
from pycityagent.ac.hub_actions import *
from pycityagent.ac.sim_actions import *

class MyLTMemory(LTMemory):
    def __init__(self, agent):
        super().__init__(agent)
        self.myattribute = 0

async def getmyattr(myLTM):
    return myLTM.myattribute

async def my_reason(wk, retrives):
    """
    Args:
    - wk (WorkingMemory): has to be
    - retrives (Optional[dict]): the retrive results according to your needs
    """
    my_attr_from_LTM = retrives['myattr']
    return (len(wk.reason.keys()), my_attr_from_LTM)

async def get_position(wk):
    sence = wk.sence # get the sence contents
    positions = sence['positions']
    longlat = positions[0]['longlat']
    return [longlat[0], longlat[1]]

def persis(wk, myltm:MyLTMemory):
    """
    Args:
    - wk (WorkingMemory): has to be
    - myltm (LTMemoey): the source LTMemory
    """
    myltm.myattribute = wk.Reason['reason_result'][0]

async def weathergo(wk):
    """
    Args:
    - wk (WorkingMemory): has to be
    """
    if wk.Reason['reason_result'][1] > 2:
        return True
    return False

async def main():
    with open('config_template.yaml', 'r') as file:
            config = yaml.safe_load(file)
    sim = pycityagent.Simulator(config['citysim_request'])

    # * create a template func agent
    id = "your agent id (int)"
    agent = await sim.GetFuncAgent(id, "name of your agent")

    agent.ConnectToHub(config['apphub_request'])
    agent.Bind()

    await agent.init_position_aoi(500031330)

    # * Soul配置: soul configuration
    llmConfig = LLMConfig(config['llm_request'])
    soul = UrbanLLM(llmConfig)
    agent.add_soul(soul)

    # * Image配置: agent image configuration
    agent.Image.get_profile()
    agent.Image.load_scratch("func_agent_scratch.json")
    print(agent.Image.get_profile())

    # * state transformer配置: State transformer configuration
    agent.StateTransformer.reset_state_transformer(['state_1', 'state_2'], 'state_1')
    agent.StateTransformer.add_transition(trigger='go_state_2', source='state_1', dest='state_2', before=None, after=None)
    agent.StateTransformer.add_transition('go_state_1', 'state_2', 'state_1')

    # * Sence配置——配置感知内容以及距离: Sence configuration, including sence contents and radius
    agent.sence_config(['poi', 'position', 'streetview'], 300)
    await agent.Brain.Sence.Sence()
    print(agent.Brain.Sence.sence_buffer)

    # * Memory配置
    # LTM
    agent.Brain.Memory.add_LTM("myLTM", MyLTMemory(agent))

    # Retrive: 信息获取
    agent.Brain.Memory.Working.retrive
    agent.Brain.Memory.Working.reset_retrive()
    get_my_attribute = MemoryRetrive('myLTM', 'myattr', getmyattr, "used to get my attribute")
    print(get_my_attribute)
    agent.Brain.Memory.Working.add_retrive("getLTMattr", get_my_attribute)

    # Reason
    agent.Brain.Memory.Working.reset_reason()
    myReason = MemoryReason("reason_result", my_reason, "just a simple reason", [get_my_attribute])
    getLonglat = MemoryReason("position", get_position, "get a reachable position")
    agent.Brain.Memory.Working.add_reason('state_1', myReason)
    agent.Brain.Memory.Working.add_reason('state_1', getLonglat)

    # This is a example program, normaly speaking, you has no need to copy the sence buffer by yourself
    agent.Brain.Memory.Working.sence = agent.Brain.Sence.sence_buffer
    await agent.Brain.Memory.Working.runReason()
    print(agent.Brain.Memory.Working.Reason)

    # Persistence
    agent.Brain.Memory.Working.reset_persistence()
    mypersis = MemoryPersistence('myLTM', persis, "just a simple persistence")
    agent.Brain.Memory.Working.add_persistence(mypersis)

    # * Command Controller配置
    agent.CommandController.reset_cc()
    myCommand = Command('go_state_2', weathergo)
    agent.CommandController.insert_command(['state_1'], myCommand)
    command_result = await agent.CommandController.Run()
    print(command_result)

    # trigger the command —— state transition
    agent.StateTransformer.machine.trigger(command_result)

    # * Action Controller配置: Action controller configuration
    agent.ActionController.reset_ac()
    myAction = PositionUpdate(agent, 'position')
    agent.ActionController.add_actions('state_1', myAction)
    await agent.ActionController.Run()

if __name__ == '__main__':
    asyncio.run(main())
