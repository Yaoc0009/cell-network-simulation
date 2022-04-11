from enum import Enum, auto

class Event_type(Enum):
    """
    Enum for the different events that can occur.
    """
    CALL_INITIATION = auto()
    CALL_TERMINATION = auto()
    CALL_HANDOVER = auto()

class FCA_scheme(Enum):
    """
    Enum for the different FCA Schemes.
    """
    NO_RESERVATION = auto()
    ONE_RESERVATION = auto()
    TWO_RESERVATION = auto()
    THREE_RESERVATION = auto()

class Direction(Enum):
    """
    Enum for the different directions of a car.
    """
    LEFT = auto()
    RIGHT = auto()

class Station:
    """
    Class for a station.
    """
    def __init__(self, station, channels, reserved_channels):
        self.station = station
        self.channels = channels
        self.reserved_channels = reserved_channels

    def allocate_channel(self):
        """
        Allocates a channel from the available channels.
        """
        if self.channels > 0:
            self.channels -= 1
            return True
        else:
            return False

    def deallocate_channel(self):
        """
        Deallocates a channel from the available channels.
        """
        self.channels += 1

    def call_init_check(self):
        """
        Checks if a call can be initiated from the station.
        """
        return self.channels - self.reserved_channels > 0

    def call_handover_check(self):
        """
        Checks if a call can be handed over from the station.
        """
        return self.channels > 0
    
class Event:
    """
    Class for an event.
    """
    def __init__(self, type, time):
        self.type = type
        self.time = time

class Call_initiation(Event):
    """
    Class for a call initiation event.
    """
    def __init__(self, time, station, duration, speed, position, direction):
        super().__init__(Event_type.CALL_INITIATION, time)
        self.station = station
        self.duration = duration
        self.speed = speed
        self.position = position
        self.direction = direction

class Call_termination(Event):
    """
    Class for a call termination event.
    """
    def __init__(self, time, station):
        super().__init__(Event_type.CALL_TERMINATION, time)
        self.station = station

class Call_handover(Event):
    """
    Class for a call handover event.
    """
    def __init__(self, time, station, duration, speed, direction):
        super().__init__(Event_type.CALL_HANDOVER, time)
        self.station = station
        self.duration = duration
        self.speed = speed
        self.direction = direction