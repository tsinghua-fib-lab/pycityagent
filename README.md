# Pycityagent

# Table of Contents
* [Introduction](#Introduction)
	* [The Whole Framework of CityAgent](#The-Whole-Framework-of-CityAgent)
	* [The Workflow of CityAgent](#The-Workflow-of-CityAgent)
* [Hands On - By An Easy Demo](#Hands-On---By-An-Easy-Demo)

<!-- TOC -->

## Introduction
### Framework of CityAgent
- ![framwork](./static/framework.png)

### Workflow of CityAgent
- ![workflow](./static/workflow.png)

## Hands On - By An Easy Demo
### Apply for your App
- You first need to register your account in the [Opencity website](https://opencity.fiblab.net/)
- Login to the console, create your own app.
- Get your app_id and app_secret
    - ![app](./static/app.png)

### Get your Config
- There are three parts of a config file: **llm_request**, **citysim_request** and **apphub_request**
```yaml
llm_request:
  text_request:
    request_type: qwen
    api_key: xxx
    model: xxx
  img_understand_request:
    request_type: qwen
    api_key: xxx
    model: xxx
  img_generate_request:
    request_type: qwen
    api_key: xxx
    model: xxx

citysim_request:
  simulator: 
    server: https://api-opencity-2x.fiblab.net:58081
  map_request:
    mongo_coll: map_beijing_extend_20240205
    cache_dir: ./cache
  streetview_request:
    engine: baidumap / googlemap
    mapAK: your baidumap AK (if baidumap)
    proxy: your googlemap proxy (if googlemap, optional)

apphub_request:
  hub_url: https://api-opencity-2x.fiblab.net:58080
  app_id: your APP ID
  app_secret: your APP Secret
  profile_image: the profile image of your agent
```
- Forget about **citysim_request**, let's focus on the other two.

#### LLM_REQUEST
- As you can tell, the whole CityAgent is based on the LLM, by now, there are three different parts of config items: **text_request**, **img_understand_request** and **img_generate_request**
- By now, we support [**qwen**](https://tongyi.aliyun.com/) and [**openai**](https://openai.com/)
    - `Notice: Our environments are basically conducted with qwen. If you prefer to use openai, then you may encounter hardships. AND fell free to issue us.`
- Get your **api_key** and chooce your **model**s

### CITYSIM_REQUEST
- There are no need to change the 'simulator' and 'map_request' config
- 'streetview_request': this is the config used for streetview
  - By now, we support 'baidumap' and 'googlemap'
  - If you use 'baidumap', then you need to apply for a mapAK
  - If you use 'googlemap', then you can config your own proxy by 'proxy' attribute

#### APPHUB_REQUEST
- This is basically used to connect with the backend.
- Put your **app_id** and **app_secret** here.

### Installation
- Install from **pip** easily.
```shell
pip install pycityagent
```

### CODE and RUN
- Check the **example** folder and copy files from it (`Remember replace the config file`)
- Look at the Demo:
```python
import yaml
from pycityagent.simulator import Simulator
from pycityagent.urbanllm import LLMConfig, UrbanLLM
import asyncio
import time

async def main():
    # load your config
    with open('config_template.yaml', 'r') as file:
        config = yaml.safe_load(file)
    
    # get the simulator object
    smi = Simulator(config['citysim_request'])
    
    # get the person by person_id, return agent
    agent = await smi.GetAgent("name_of_agent", 8)

    # Help you build unique agent by scratch/profile
    agent.Image.load_scratch('scratch_template.json')

    # Load Memory and assist the agent to understand "Opencity"
    agent.Brain.Memory.Spatial.MemoryLoad('spatial_knowledge_template.json')
    agent.Brain.Memory.Social.MemoryLoad('social_background_template.json')

    # Connect to apphub so you can interact with your agent in front end
    agent.ConnectToHub(config['apphub_request'])

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
```

### Congratulations
- Following this "Hands On" guide, you have easily created an agent by your hand! 
- You can observe your AGENT in your console or in the [Opencity website](https://opencity.fiblab.net/).
- HAVE FUN WITH IT!