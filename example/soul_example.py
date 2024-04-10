import yaml
from pycityagent.simulator import Simulator
from pycityagent.urbanllm import LLMConfig, UrbanLLM
import asyncio
import time

async def main():
    # load your config
    with open('config_template.yaml', 'r') as file:
        config = yaml.safe_load(file)

    # Creat the soul (a LLM processor actually)
    llmConfig = LLMConfig(config['llm_request'])
    soul = UrbanLLM(llmConfig)

    # text request
    resp = soul.text_request(
        [
            {'role': 'user', 'content': 'hello'}
        ]
    )
 
    """
    Image generation

    Args:
    - prompt: your generation prompt
    - size: image size, default 512 * 512, check the api doc of your chosen LLM provider for more choises
    - quantity: number of images, default 1

    Returns:
    - list[Image]
    """
    images = soul.img_generate(prompt="A cute cat", size='512 * 512', quantity=1)

    """
    Image understanding

    Args:
    - img_path (str): the absolute path of target image
    - prompt (str): help the LLM to understand the image

    Returns:
    - str
    """
    ud = soul.img_understand(img_path="the_absolute_path_of_target_image", prompt="your helping prompt")

if __name__ == '__main__':
    asyncio.run(main())