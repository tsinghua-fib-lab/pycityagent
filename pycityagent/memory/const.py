from .type import (BikeAttribute, BusAttribute, PedestrianAttribute,
                   PersonAttribute, Position, Status, VehicleAttribute)

PROFILE_ATTRIBUTES = {
    "gender": str(),
    "age": float(),
    "education": str(),
    "skill": str(),
    "occupation": str(),
    "family_consumption": str(),
    "consumption": str(),
    "personality": str(),
    "income": str(),
    "residence": str(),
    "race": str(),
    "religion": str(),
    "marital_status": str(),
}

STATE_ATTRIBUTES = {
    # base
    "id": int(),
    "attribute": PersonAttribute(),
    "home": Position(),
    "work": Position(),
    "schedules": [],
    "vehicle_attribute": VehicleAttribute(),
    "bus_attribute": BusAttribute(),
    "pedestrian_attribute": PedestrianAttribute(),
    "bike_attribute": BikeAttribute(),
    # motion
    "status": Status.STATUS_UNSPECIFIED,
    "position": Position(),
    "v": float(),
    "direction": float(),
    "activity": str(),
    "l": float(),
}

SELF_DEFINE_PREFIX = "self_define_"
