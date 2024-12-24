from pycityproto.city.person.v2.motion_pb2 import Status

PROFILE_ATTRIBUTES = {
    "name": str(),
    "gender": str(),
    "age": float(),
    "education": str(),
    "skill": str(),
    "occupation": str(),
    "family_consumption": str(),
    "consumption": str(),
    "personality": str(),
    "income": str(),
    "currency": float(),
    "residence": str(),
    "race": str(),
    "religion": str(),
    "marital_status": str(),
}

STATE_ATTRIBUTES = {
    # base
    "id": -1,
    "attribute": dict(),
    "home": dict(),
    "work": dict(),
    "schedules": [],
    "vehicle_attribute": dict(),
    "bus_attribute": dict(),
    "pedestrian_attribute": dict(),
    "bike_attribute": dict(),
    # motion
    "status": Status.STATUS_UNSPECIFIED,
    "position": dict(),
    "v": float(),
    "direction": float(),
    "activity": str(),
    "l": float(),
}

SELF_DEFINE_PREFIX = "self_define_"

TIME_STAMP_KEY = "_timestamp"
