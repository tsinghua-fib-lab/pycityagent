import json
import logging

from agentsociety.environment.simulator import Simulator
from agentsociety.llm import LLM
from agentsociety.memory import Memory
from agentsociety.workflow.block import Block
from agentsociety.workflow.prompt import FormatPrompt

logger = logging.getLogger("agentsociety")


def extract_json(output_str):
    try:
        # Find the positions of the first '{' and the last '}'
        start = output_str.find("{")
        end = output_str.rfind("}")

        # Extract the substring containing the JSON
        json_str = output_str[start : end + 1]

        # Convert the JSON string to a dictionary
        return json_str
    except (ValueError, json.JSONDecodeError) as e:
        logger.warning(f"Failed to extract JSON: {e}")
        return None


class CognitionBlock(Block):
    configurable_fields = ["top_k"]
    default_values = {"top_k": 20}
    fields_description = {
        "top_k": "Number of most relevant memories to return, defaults to 20"
    }

    def __init__(self, llm: LLM, memory: Memory, simulator: Simulator):
        super().__init__("CognitionBlock", llm=llm, memory=memory, simulator=simulator)
        self.top_k = 20
        self.last_check_time = 0

    async def set_status(self, status):
        for key in status:
            await self.memory.status.update(key, status[key])
        return

    async def attitude_update(self):
        """Cognition - attitude update workflow"""
        attitude = await self.memory.status.get("attitude")
        prompt_data = {
            "gender": await self.memory.status.get("gender"),
            "age": await self.memory.status.get("age"),
            "race": await self.memory.status.get("race"),
            "religion": await self.memory.status.get("religion"),
            "marital_status": await self.memory.status.get("marital_status"),
            "residence": await self.memory.status.get("residence"),
            "occupation": await self.memory.status.get("occupation"),
            "education": await self.memory.status.get("education"),
            "personality": await self.memory.status.get("personality"),
            "consumption": await self.memory.status.get("consumption"),
            "family_consumption": await self.memory.status.get("family_consumption"),
            "income": await self.memory.status.get("income"),
            "skill": await self.memory.status.get("skill"),
            "thought": await self.memory.status.get("thought"),
            "emotion_types": await self.memory.status.get("emotion_types"),
        }
        for topic in attitude:
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
            incident_str = await self.memory.stream.search(
                query=topic, top_k=self.top_k
            )
            if incident_str:
                incident_prompt = "Today, these incidents happened:"
                incident_prompt += incident_str
            else:
                incident_prompt = "No incidents happened today."
            previous_attitude = str(attitude[topic])  # Convert to string
            problem_prompt = (
                f"You need to decide your attitude towards topic: {topic}, "
                f"which you previously rated your attitude towards this topic as: {previous_attitude} "
                "(0 meaning oppose, 10 meaning support). "
                'Please return a new attitude rating (0-10, smaller meaning oppose, larger meaning support) in JSON format, and explain, e.g. {{"attitude": 5}}'
            )
            question_prompt = description_prompt + incident_prompt + problem_prompt
            question_prompt = FormatPrompt(question_prompt)
            emotion = await self.memory.status.get("emotion")
            sadness = emotion["sadness"]
            joy = emotion["joy"]
            fear = emotion["fear"]
            disgust = emotion["disgust"]
            anger = emotion["anger"]
            surprise = emotion["surprise"]
            prompt_data["sadness"] = sadness
            prompt_data["joy"] = joy
            prompt_data["fear"] = fear
            prompt_data["disgust"] = disgust
            prompt_data["anger"] = anger
            prompt_data["surprise"] = surprise

            question_prompt.format(**prompt_data)
            evaluation = True
            response: dict = {}
            for retry in range(10):
                try:
                    _response = await self.llm.atext_request(
                        question_prompt.to_dialog(), timeout=300, response_format={"type": "json_object"}
                    )
                    response = json.loads(extract_json(_response))  # type:ignore
                    evaluation = False
                    break
                except:
                    pass
            if evaluation:
                raise Exception(f"Request for attitude:{topic} update failed")
            attitude[topic] = response["attitude"]
        await self.memory.status.update("attitude", attitude)

    async def thought_update(self):
        """Cognition - thought update workflow"""
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
        incident_str = await self.memory.stream.search_today(top_k=20)
        if incident_str:
            incident_prompt = "Today, these incidents happened:\n" + incident_str
        else:
            incident_prompt = "No incidents happened today."
        question_prompt = """
            Please review what happened today and share your thoughts and feelings about it.
            Consider your current emotional state and experiences, then:
            1. Summarize your thoughts and reflections on today's events
            2. Choose one word that best describes your current emotional state from: Joy, Distress, Resentment, Pity, Hope, Fear, Satisfaction, Relief, Disappointment, Pride, Admiration, Shame, Reproach, Liking, Disliking, Gratitude, Anger, Gratification, Remorse, Love, Hate.
            Return in JSON format, e.g. {{"thought": "Currently nothing good or bad is happening, I think ...."}}"""
        question_prompt = description_prompt + incident_prompt + question_prompt
        question_prompt = FormatPrompt(question_prompt)
        emotion = await self.memory.status.get("emotion")
        sadness = emotion["sadness"]
        joy = emotion["joy"]
        fear = emotion["fear"]
        disgust = emotion["disgust"]
        anger = emotion["anger"]
        surprise = emotion["surprise"]
        question_prompt.format(
            gender=await self.memory.status.get("gender"),
            age=await self.memory.status.get("age"),
            race=await self.memory.status.get("race"),
            religion=await self.memory.status.get("religion"),
            marital_status=await self.memory.status.get("marital_status"),
            residence=await self.memory.status.get("residence"),
            occupation=await self.memory.status.get("occupation"),
            education=await self.memory.status.get("education"),
            personality=await self.memory.status.get("personality"),
            consumption=await self.memory.status.get("consumption"),
            family_consumption=await self.memory.status.get("family_consumption"),
            income=await self.memory.status.get("income"),
            skill=await self.memory.status.get("skill"),
            sadness=sadness,
            joy=joy,
            fear=fear,
            disgust=disgust,
            anger=anger,
            surprise=surprise,
            emotion=await self.memory.status.get("emotion"),
            thought=await self.memory.status.get("thought"),
            emotion_types=await self.memory.status.get("emotion_types"),
        )

        evaluation = True
        response: dict = {}
        for retry in range(10):
            try:
                _response = await self.llm.atext_request(
                    question_prompt.to_dialog(), timeout=300, response_format={"type": "json_object"}
                )
                response = json.loads(extract_json(_response))  # type:ignore
                evaluation = False
                break
            except:
                pass
        if evaluation:
            raise Exception("Request for cognition update failed")

        thought = str(response["thought"])
        await self.memory.status.update("thought", thought)
        await self.memory.stream.add_cognition(description=thought)

        return thought

    async def cross_day(self):
        """Cognition - cross day workflow"""
        time = await self.simulator.get_simulator_second_from_start_of_day()
        if self.last_check_time == 0:
            self.last_check_time = time
            return False
        if time < self.last_check_time:
            self.last_check_time = time
            return True
        self.last_check_time = time
        return False

    async def forward(self):
        """Cognition workflow: Daily update"""
        # cognition update: thought and attitude
        if await self.cross_day():
            await self.thought_update()
            await self.attitude_update()

    async def emotion_update(self, incident):
        """Cognition - emotion update workflow"""
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

        incident_prompt = f"{incident}"  # waiting for incident port
        question_prompt = """
            Please reconsider your emotion intensities: 
            sadness, joy, fear, disgust, anger, surprise (0 meaning not at all, 10 meaning very much).
            Return in JSON format, e.g. {{"sadness": 5, "joy": 5, "fear": 5, "disgust": 5, "anger": 5, "surprise": 5, "conclusion": "I feel ...", "word": "Relief"}}"""
        question_prompt = description_prompt + incident_prompt + question_prompt
        question_prompt = FormatPrompt(question_prompt)
        emotion = await self.memory.status.get("emotion")
        sadness = emotion["sadness"]
        joy = emotion["joy"]
        fear = emotion["fear"]
        disgust = emotion["disgust"]
        anger = emotion["anger"]
        surprise = emotion["surprise"]
        question_prompt.format(
            gender=await self.memory.status.get("gender"),
            age=await self.memory.status.get("age"),
            race=await self.memory.status.get("race"),
            religion=await self.memory.status.get("religion"),
            marital_status=await self.memory.status.get("marital_status"),
            residence=await self.memory.status.get("residence"),
            occupation=await self.memory.status.get("occupation"),
            education=await self.memory.status.get("education"),
            personality=await self.memory.status.get("personality"),
            consumption=await self.memory.status.get("consumption"),
            family_consumption=await self.memory.status.get("family_consumption"),
            income=await self.memory.status.get("income"),
            skill=await self.memory.status.get("skill"),
            sadness=sadness,
            joy=joy,
            fear=fear,
            disgust=disgust,
            anger=anger,
            surprise=surprise,
            emotion=await self.memory.status.get("emotion"),
            thought=await self.memory.status.get("thought"),
            emotion_types=await self.memory.status.get("emotion_types"),
        )

        evaluation = True
        response: dict = {}
        for retry in range(10):
            try:
                _response = await self.llm.atext_request(
                    question_prompt.to_dialog(), timeout=300, response_format={"type": "json_object"}
                )
                response = json.loads(extract_json(_response))  # type:ignore
                evaluation = False
                break
            except Exception as e:
                logger.warning(f"Request for cognition update failed: {e}")
                pass
        if evaluation:
            raise Exception("Request for cognition update failed")

        await self.memory.status.update(
            "emotion",
            {
                "sadness": int(response["sadness"]),
                "joy": int(response["joy"]),
                "fear": int(response["fear"]),
                "disgust": int(response["disgust"]),
                "anger": int(response["anger"]),
                "surprise": int(response["surprise"]),
            },
        )
        await self.memory.status.update("emotion_types", str(response["word"]))
        return response["conclusion"]
