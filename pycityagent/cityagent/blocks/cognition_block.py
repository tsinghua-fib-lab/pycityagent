from pycityagent.llm.llm import LLM
from pycityagent.workflow.block import Block
from pycityagent.memory import Memory
from pycityagent.environment.simulator import Simulator
from pycityagent.workflow.prompt import FormatPrompt
import json
import logging
logger = logging.getLogger("pycityagent")

def extract_json(output_str):
    try:
        # Find the positions of the first '{' and the last '}'
        start = output_str.find('{')
        end = output_str.rfind('}')
        
        # Extract the substring containing the JSON
        json_str = output_str[start:end+1]
        
        # Convert the JSON string to a dictionary
        return json_str
    except (ValueError, json.JSONDecodeError) as e:
        logger.warning(f"Failed to extract JSON: {e}")
        return None

class CognitionBlock(Block):
    def __init__(self, llm: LLM, memory: Memory, simulator: Simulator):
        super().__init__("CognitionBlock", llm, memory, simulator)
        self.last_trigger_time = None
        self.time_diff = 24*60*60 # 24小时
        self.trigger_time = 0
        self.token_consumption = 0
        
    async def set_status(self, status):
        for key in status:
            await self.memory.update(key, status[key])
        return
    
    async def check_trigger(self):
        now_time = await self.simulator.get_time()
        if self.last_trigger_time is None or now_time - self.last_trigger_time > self.time_diff:
            self.last_trigger_time = now_time
            return True
        return False
    
    async def attitude_update(self, topic):
        description_prompt = """
        You are a {gender}, aged {age}, belonging to the {race} race and identifying as {religion}. 
        Your marital status is {marital_status}, and you currently reside in a {residence} area. 
        Your occupation is {occupation}, and your education level is {education}. 
        You are {personality}, with a consumption level of {consumption} and a family consumption level of {family_consumption}. 
        Your income is {income}, and you are skilled in {skill}.
        My current emotion intensities are (0 meaning not at all, 10 meaning very much):
        sadness: {sadness}, joy: {joy}, fear: {fear}, disgust: {disgust}, anger: {anger}, surprise: {surprise}.
        You have the following thoughts: {thought}.
        In the following 21 words, I have chosen {emotion_types} to represent your current status:
        Joy, Distress, Resentment, Pity, Hope, Fear, Satisfaction, Relief, Disappointment, Pride, Admiration, Shame, Reproach, Liking, Disliking, Gratitude, Anger, Gratification, Remorse, Love, Hate.
        """
        incident_list = await self.memory.get("incident")
        if incident_list:
            incident_prompt = "Today, these incidents happened:"
            for incident in incident_list:
                incident_prompt += incident
        else:
            incident_prompt = "No incidents happened today."
        attitude = await self.memory.get("attitude")
        if topic in attitude:
            previous_attitude = str(attitude[topic])  # Convert to string
            problem_prompt = (
                f"You need to decide your attitude towards topic: {topic}, "
                f"which you previously rated your attitude towards this topic as: {previous_attitude} "
                "(0 meaning oppose, 10 meaning support). "
                "Please return a new attitude rating (0-10, smaller meaning oppose, larger meaning support) in JSON format, and explain, e.g. {{\"attitude\": 5}}"
            )
        else:
            problem_prompt = (
                f"You need to decide your attitude towards topic: {topic}, "
                "which you have not rated your attitude towards this topic yet. "
                "(0 meaning oppose, 10 meaning support). "
                "Please return a new attitude rating (0-10, smaller meaning oppose, larger meaning support) in JSON format, and explain, e.g. {{\"attitude\": 5}}"
            )
        question_prompt = description_prompt + incident_prompt + problem_prompt
        question_prompt = FormatPrompt(question_prompt)
        emotion = await self.memory.get("emotion")
        sadness = emotion["sadness"]
        joy = emotion["joy"]
        fear = emotion["fear"]
        disgust = emotion["disgust"]
        anger = emotion["anger"]
        surprise = emotion["surprise"]
        
        question_prompt.format(
            gender=await self.memory.get("gender"),
            age=await self.memory.get("age"),
            race=await self.memory.get("race"),
            religion=await self.memory.get("religion"),
            marital_status=await self.memory.get("marital_status"),
            residence=await self.memory.get("residence"),
            occupation=await self.memory.get("occupation"),
            education=await self.memory.get("education"),
            personality=await self.memory.get("personality"),
            consumption=await self.memory.get("consumption"),
            family_consumption=await self.memory.get("family_consumption"),
            income=await self.memory.get("income"),
            skill=await self.memory.get("skill"),
            sadness=sadness,
            joy=joy,
            fear=fear,
            disgust=disgust,
            anger=anger,
            surprise=surprise,
            thought=await self.memory.get("thought"),
            emotion_types=await self.memory.get("emotion_types")
        )
        evaluation = True
        for retry in range(10):
            try:
                response = await self.llm.atext_request(question_prompt.to_dialog(), timeout=300)
                response = json.loads(extract_json(response))
                evaluation = False
                break
            except:
                pass
        if evaluation:
            raise f"Request for attitude:{topic} update failed"
        logger.info(f"""Cognition updated attitude:{topic}:
            attitude: {response['attitude']}""")
        attitude[topic] = response["attitude"]
        await self.memory.update("attitude", attitude)
        return
    
    async def forward(self): #每日结算
        whether_trigger = await self.check_trigger()
        if not whether_trigger:
            return
        self.trigger_time += 1
        consumption_start = self.llm.prompt_tokens_used + self.llm.completion_tokens_used

        description_prompt = """
        You are a {gender}, aged {age}, belonging to the {race} race and identifying as {religion}. 
        Your marital status is {marital_status}, and you currently reside in a {residence} area. 
        Your occupation is {occupation}, and your education level is {education}. 
        You are {personality}, with a consumption level of {consumption} and a family consumption level of {family_consumption}. 
        Your income is {income}, and you are skilled in {skill}.
        My current emotion intensities are (0 meaning not at all, 10 meaning very much):
        sadness: {sadness}, joy: {joy}, fear: {fear}, disgust: {disgust}, anger: {anger}, surprise: {surprise}.
        You have the following thoughts: {thought}.
        In the following 21 words, I have chosen {emotion_types} to represent your current status:
        Joy, Distress, Resentment, Pity, Hope, Fear, Satisfaction, Relief, Disappointment, Pride, Admiration, Shame, Reproach, Liking, Disliking, Gratitude, Anger, Gratification, Remorse, Love, Hate.
        """
        incident_list = await self.memory.get("incident")
        if incident_list:
            incident_prompt = "Today, these incidents happened:"
            for incident in incident_list:
                incident_prompt += incident
        else:
            incident_prompt = "No incidents happened today."
        question_prompt = """
            Please reconsider your emotion intensities: 
            sadness, joy, fear, disgust, anger, surprise (0 meaning not at all, 10 meaning very much).
            Also summerize you current thoughts, and choose a word to describe your status: Joy, Distress, Resentment, Pity, Hope, Fear, Satisfaction, Relief, Disappointment, Pride, Admiration, Shame, Reproach, Liking, Disliking, Gratitude, Anger, Gratification, Remorse, Love, Hate.
            Return in JSON format, e.g. {{"sadness": 5, "joy": 5, "fear": 5, "disgust": 5, "anger": 5, "surprise": 5, "thought": "Currently nothing good or bad is happening, I think ....", "word": "Relief"}}"""
        question_prompt = description_prompt + incident_prompt + question_prompt
        question_prompt = FormatPrompt(question_prompt)
        emotion = await self.memory.get("emotion")
        sadness = emotion["sadness"]
        joy = emotion["joy"]
        fear = emotion["fear"]
        disgust = emotion["disgust"]
        anger = emotion["anger"]
        surprise = emotion["surprise"]
        question_prompt.format(
            gender=await self.memory.get("gender"),
            age=await self.memory.get("age"),
            race=await self.memory.get("race"),
            religion=await self.memory.get("religion"),
            marital_status=await self.memory.get("marital_status"),
            residence=await self.memory.get("residence"),
            occupation=await self.memory.get("occupation"),
            education=await self.memory.get("education"),
            personality=await self.memory.get("personality"),
            consumption=await self.memory.get("consumption"),
            family_consumption=await self.memory.get("family_consumption"),
            income=await self.memory.get("income"),
            skill=await self.memory.get("skill"),
            sadness=sadness,
            joy=joy,
            fear=fear,
            disgust=disgust,
            anger=anger,
            surprise=surprise,
            emotion=await self.memory.get("emotion"),
            thought=await self.memory.get("thought"),
            emotion_types=await self.memory.get("emotion_types")
        )
        
        evaluation = True
        for retry in range(10):
            try:
                response = await self.llm.atext_request(question_prompt.to_dialog(), timeout=300)
                response = json.loads(extract_json(response))
                evaluation = False
                break
            except:
                pass
        if evaluation:
            raise Exception("Request for cognition update failed")
        logger.info(f"""Cognition updated emotion intensities:
            sadness: {response['sadness']},
            joy: {response['joy']},
            fear: {response['fear']},
            disgust: {response['disgust']},
            anger: {response['anger']},
            surprise: {response['surprise']}"
            thought: {response['thought']}
            emotion_types: {response['word']}""")
        
        await self.memory.update("incident", [])
        await self.memory.update("emotion", {"sadness": int(response["sadness"]), "joy": int(response["joy"]), "fear": int(response["fear"]), "disgust": int(response["disgust"]), "anger": int(response["anger"]), "surprise": int(response["surprise"])})
        await self.memory.update("thought", str(response["thought"]))
        await self.memory.update("emotion_types", str(response["word"]))

        consumption_end = self.llm.prompt_tokens_used + self.llm.completion_tokens_used
        self.token_consumption += consumption_end - consumption_start
        return
    
    async def emotion_update(self, incident): #每日结算
        whether_trigger = await self.check_trigger()
        if not whether_trigger:
            return

        description_prompt = """
        You are a {gender}, aged {age}, belonging to the {race} race and identifying as {religion}. 
        Your marital status is {marital_status}, and you currently reside in a {residence} area. 
        Your occupation is {occupation}, and your education level is {education}. 
        You are {personality}, with a consumption level of {consumption} and a family consumption level of {family_consumption}. 
        Your income is {income}, and you are skilled in {skill}.
        My current emotion intensities are (0 meaning not at all, 10 meaning very much):
        sadness: {sadness}, joy: {joy}, fear: {fear}, disgust: {disgust}, anger: {anger}, surprise: {surprise}.
        You have the following thoughts: {thought}.
        In the following 21 words, I have chosen {emotion_types} to represent your current status:
        Joy, Distress, Resentment, Pity, Hope, Fear, Satisfaction, Relief, Disappointment, Pride, Admiration, Shame, Reproach, Liking, Disliking, Gratitude, Anger, Gratification, Remorse, Love, Hate.
        """

        incident_prompt = incident  #waiting for incident port
        question_prompt = """
            Please reconsider your emotion intensities: 
            sadness, joy, fear, disgust, anger, surprise (0 meaning not at all, 10 meaning very much).
            Return in JSON format, e.g. {{"sadness": 5, "joy": 5, "fear": 5, "disgust": 5, "anger": 5, "surprise": 5}}"""
        question_prompt = description_prompt + incident_prompt + question_prompt
        question_prompt = FormatPrompt(question_prompt)
        emotion = await self.memory.get("emotion")
        sadness = emotion["sadness"]
        joy = emotion["joy"]
        fear = emotion["fear"]
        disgust = emotion["disgust"]
        anger = emotion["anger"]
        surprise = emotion["surprise"]
        question_prompt.format(
            gender=await self.memory.get("gender"),
            age=await self.memory.get("age"),
            race=await self.memory.get("race"),
            religion=await self.memory.get("religion"),
            marital_status=await self.memory.get("marital_status"),
            residence=await self.memory.get("residence"),
            occupation=await self.memory.get("occupation"),
            education=await self.memory.get("education"),
            personality=await self.memory.get("personality"),
            consumption=await self.memory.get("consumption"),
            family_consumption=await self.memory.get("family_consumption"),
            income=await self.memory.get("income"),
            skill=await self.memory.get("skill"),
            sadness=sadness,
            joy=joy,
            fear=fear,
            disgust=disgust,
            anger=anger,
            surprise=surprise,
            emotion=await self.memory.get("emotion"),
            thought=await self.memory.get("thought"),
            emotion_types=await self.memory.get("emotion_types")
        )
        
        evaluation = True
        for retry in range(10):
            try:
                response = await self.llm.atext_request(question_prompt.to_dialog(), timeout=300)
                response = json.loads(extract_json(response))
                evaluation = False
                break
            except Exception as e:
                print(e)
                pass
        if evaluation:
            raise Exception("Request for cognition update failed")
        logger.info(f"""Cognition updated emotion intensities:
            sadness: {response['sadness']},
            joy: {response['joy']},
            fear: {response['fear']},
            disgust: {response['disgust']},
            anger: {response['anger']},
            surprise: {response['surprise']}""")

        await self.memory.update("emotion", {"sadness": int(response["sadness"]), "joy": int(response["joy"]), "fear": int(response["fear"]), "disgust": int(response["disgust"]), "anger": int(response["anger"]), "surprise": int(response["surprise"])})
        return