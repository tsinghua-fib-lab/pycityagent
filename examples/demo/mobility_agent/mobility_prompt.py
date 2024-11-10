from .utils import *

INTENTION_GENERATION = """
I'm a {gender}, my education level is {education}, my consumption level is {consumption} and my education level is {education}.
Today is {day}, now is {time}.
What my should do next?
Please select from ['eat', 'have breakfast', 'have lunch', 'have dinner', 'do shopping', 'do sports', 'excursion', 'leisure or entertainment', 'medical treatment', 'handle the trivialities of life', 'banking and financial services', 'government and political services', 'cultural institutions and events']
Your ouput only contains one of the above actions without any other words.
"""

# time is a str, like "10:00", add a hour to time
def time_add(time):
    hour, minute = time.split(":")
    hour = int(hour) + 1
    return f"{hour}:{minute}"

async def get_place(context):
    intention = await context.get('intention')
    nowPlace = await context.get('nowPlace')
    map = await context.get("map")

    eventId = getDirectEventID(intention)
    POIs = event2poi_gravity(map, eventId, nowPlace) 
    options = list(range(len(POIs)))
    probabilities = [item[2] for item in POIs]
    sample = np.random.choice(options, size=1, p=probabilities)  # 根据计算出来的概率值进行采样
    nextPlace = POIs[sample[0]]
    nextPlace = (nextPlace[0], nextPlace[1])
    time = time_add(await context.get("time"))
    print(f"time: {time}, nextPlace: {nextPlace}")

    return {"nowPlace": nextPlace, "time": time}
    