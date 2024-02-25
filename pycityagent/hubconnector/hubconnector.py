from typing import Optional
import geojson
from pycitysim.apphub import AppHubClient, AgentMessage, UserMessage
import PIL.Image as Image
import traceback

class HubConnector:
    """
    AppHub连接组件
    AppHub connection module
    """
    def __init__(self, hub_url:str=None, app_id:int=None, app_secret:str=None, agent=None, profile_img:str=None) -> None:
        if hub_url == None:
            self._client = None
        else:
            self._client = AppHubClient(
                            app_hub_url=hub_url,
                            app_id=app_id,
                            app_secret=app_secret
                        )
        if agent == None:
            self._agent = None
            self._agent_id = None
        else:
            self._agent = agent
            try:
                self._agent_id = self._client.bind_person(
                    self._agent.base['id'], 
                    self._agent.agent_name, 
                    Image.open(profile_img)
                )
            except Exception as e:
                traceback.print_exc()
                print(e)
                self._agent_id = 7
        self.messageBuffer:list[AgentMessage] = []
        """
        用于存储历史前端交互信息
        Used to store the history message in frontend
        """

    def ConnectToHub(self, hub_url:str, app_id:int, app_secret:str):
        """
        连接AppHub
        Connect with AppHub

        Args:
        - hub_url (str): the url of AppHub
        - app_id (int): the allocated app_id
        - app_secret (str): the allocated app_secret
        """
        self._client = AppHubClient(
            app_hub_url=hub_url,
            app_id=app_id,
            app_secret=app_secret
        )

    def BindAgent(self, agent, profile_img:str):
        """
        绑定Agent
        Bind an Agent through AppHub

        Args:
        - agent (Agent): the Agent needs to be bind with
        - profile_img (str) : the path of profile_img, which will be shown in frontend and dashboard
        """
        if self._client == None:
            print("Not Connect To AppHub Yet")
            return
        self._agent = agent
        self._agent_id = self._client.bind_person(
            self._agent.base['id'], 
            self._agent.agent_name, 
            Image.open(profile_img)
        )

    def Update(self, messages:Optional[list[AgentMessage]]=None, streetview:Image=None, longlat:list[float]=None, pop:str=None):
        """
        交互更新
        FrontEnd Related Update
        Note: This function is used by the lib developer. Normally, the user has no need to use this function

        Default Action: no message, no streetview, locate based on the Agent's position, Agent's name as pop

        Args:
        - messages (Optional[list[AgentMessage]]): 
            - 需要传递到前端侧边栏的消息. Messsages that will be shown in the message bar in frontend
            - 默认为None(即当前无需传递消息). Default: None(i.e. No new messages need to be shown in frontend)
        - streetview (PIL.Image.Image): 
            - 街景图片. Streetview Image
            - 默认为None(即本次更新不展示街景). Default: None(i.e. No streetview in this update)
        - longlat (list(float)): 
            - 经纬度坐标, 用于前端定位, 默认为None(即根据Agent当前位置进行设置). The longitude and latitude, which helps locate the Agent, default: None(i.e. locate the Agent by the current position of agent)
            - 只有在有特殊展示需求的情况下才设置该参数. Only when you have special display requirements, you will set the attribute
        - pop (str):
            - 气泡信息. The pop message
            - 默认为None(即没有气泡信息). Default: None(i.e. No pop message)
        """
        if self._client == None:
            print("AppHub: Not Bind Agent Yet")
            return
        else:
            pop_ = self._agent.agent_name
            if pop != None:
                pop_ = self._agent.agent_name + ": " + pop
            longlat_ = [self._agent.motion['position']['longlat_position']['longitude'], self._agent.motion['position']['longlat_position']['latitude']]
            if longlat != None:
                longlat_ = longlat
            
            self._client.update_agent_map(
                agent_id = self._agent_id, 
                lnglat = longlat_,
                street_view=streetview,
                popup=pop_
            )
            if messages != None:
                self.messageBuffer += messages
                self._client.update_agent_messages(
                    agent_id=self._agent_id,
                    messages=self.messageBuffer
                )

    def GetMessageFromHub(self) -> list[UserMessage]:
        """
        获取前端messages
        Get User messages from AppHub

        Returns:
        - list[UserMessage]
        """
        resp = self._client.fetch_user_messages(self._agent_id)
        if len(resp) > 0:
            u2a = []
            for re in resp:
                u2a.append(AgentMessage(re.id, re.timestamp, re.content, None, None))
            self.messageBuffer += u2a
        return resp