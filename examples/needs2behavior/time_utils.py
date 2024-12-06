class TimeManager:
    _instance = None
    _now_time = "08:00"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TimeManager, cls).__new__(cls)
        return cls._instance

    @classmethod
    def get_time(cls) -> str:
        return cls._now_time

    @classmethod
    def add_minutes(cls, minutes: int) -> str:
        hour, minute = map(int, cls._now_time.split(":"))
        total_minutes = hour * 60 + minute + minutes
        new_hour = total_minutes // 60
        new_minute = total_minutes % 60
        cls._now_time = f"{new_hour:02d}:{new_minute:02d}"
        return cls._now_time

    @classmethod
    def calculate_hours_difference(cls, time1: str, time2: str) -> float:
        """计算两个时间点之间的小时差"""
        h1, m1 = map(int, time1.split(":"))
        h2, m2 = map(int, time2.split(":"))
        return (h2 * 60 + m2 - (h1 * 60 + m1)) / 60.0 