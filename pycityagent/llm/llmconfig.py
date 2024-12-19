class LLMConfig:
    """
    大语言模型相关配置
    The config of LLM
    """

    def __init__(self, config: dict) -> None:
        self.config = config
        self.text = config["text_request"]
        if "api_base" in self.text.keys() and self.text["api_base"] == "None":
            self.text["api_base"] = None
        self.image_u = config["img_understand_request"]
        self.image_g = config["img_generate_request"]
