from model_helpers import *
import pandas as pd
import numpy as np

data = pd.read_excel("PCS_TEST_DETERMINSTIC.xls")
data.columns = data.columns.str.strip()

# calculate parameters for each distributions
int_arr = np.diff(data['Arrival time (sec)'])
beta_arr = np.mean(int_arr)
translation = min(data['Call duration (sec)'])
beta_dur = np.mean(data['Call duration (sec)']-translation)
mu_vel = np.mean(data['velocity (km/h)'])
std_vel = np.std(data['velocity (km/h)'])

def get_random_interarrival():
    return np.random.exponential(beta_arr)

def get_random_base_station():
    return np.random.randint(20)

def get_random_duration():
    return np.random.exponential(beta_dur) + translation

def get_random_speed():
    return np.random.normal(mu_vel, std_vel)

def get_random_direction():
    return np.random.choice([Direction.RIGHT, Direction.LEFT])

def get_random_position():
    return np.random.uniform(0, 2)

class Simulator:
    def __init__(self, scheme, total_calls, warmup_period):
        self.scheme = scheme
        self.total_calls = total_calls
        self.warmup_period = warmup_period

        # init variables
        self.current_time = 0
        self.blocked_calls = 0
        self.dropped_calls = 0
        self.generated_calls = 0
        self.new_calls = 0

        # init stations
        channels = 10
        if self.scheme == FCA_scheme.NO_RESERVATION:
            reserved_channels = 0
        elif self.scheme == FCA_scheme.ONE_RESERVATION:
            reserved_channels = 1
        elif self.scheme == FCA_scheme.TWO_RESERVATION:
            reserved_channels = 2
        elif self.scheme == FCA_scheme.THREE_RESERVATION:
            reserved_channels = 3
        self.stations = [Station(i, channels, reserved_channels) for i in range(20)]

        # init future events list
        self.future_events = []

        # generate first call initiation event
        first_call = Call_initiation(0, get_random_base_station(), get_random_duration(), get_random_speed(), get_random_position(), get_random_direction())
        self.generated_calls += 1
        # add first call initiation event to future events list
        self.future_events.append(first_call)

    # insert events in order of event.time with binary search algorithm
    def insert_event(self, event):
        # binary search algorithm
        left = 0
        right = len(self.future_events) - 1
        while left <= right:
            mid = (left + right) // 2
            if self.future_events[mid].time > event.time:
                right = mid - 1
            elif self.future_events[mid].time < event.time:
                left = mid + 1
            else:
                self.future_events.insert(mid, event)
                return
        self.future_events.insert(left, event)

    # call initiation handling function
    def handle_call_initiation(self, event):
        # calculate number of new calls after warmup period
        if self.current_time > self.warmup_period:
            self.new_calls += 1

        # get station
        station = self.stations[event.station]

        # check if call can be initiated
        if station.call_init_check():
            # allocate channel
            station.allocate_channel()

            # check direction, then determine remaining distance and next station
            if event.direction == Direction.RIGHT:
                remaining_distance = event.position
                next_station = event.station + 1
            else:
                remaining_distance = 2 - event.position
                next_station = event.station - 1

            # calculate time to next station
            time_to_next_station = (remaining_distance / event.speed) * 3600

            # if time to next station is greater than call duration, create call termination event, call is terminated. if next station is less than 0 or greater than 19, call is terminated. else call is handed over to next station
            if time_to_next_station > event.duration:
                #create call termination event`
                new_event = Call_termination(self.current_time + event.duration, event.station)
            
            elif next_station < 0 or next_station > 19:
                #create call termination event
                new_event = Call_termination(self.current_time + time_to_next_station, event.station)
            else:
                #create call handover event
                new_event = Call_handover(self.current_time + time_to_next_station, event.station, event.duration - time_to_next_station, event.speed, event.direction)

            # insert new event in future events list
            self.insert_event(new_event)

        # if call cannot be initiated and event time is after the warmup period, call is blocked
        elif self.current_time > self.warmup_period:
            self.blocked_calls += 1

    # call termination handling function
    def handle_call_termination(self, event):
        # get station
        station = self.stations[event.station]

        # release channel
        station.deallocate_channel()

    # call handover handling function
    def handle_call_handover(self, event):
        self.stations[event.station].deallocate_channel()

        # get the next station depending on direction
        if event.direction == Direction.RIGHT:
            event.station += 1
        else:
            event.station -= 1

        # get station
        station = self.stations[event.station]
        # check if call can be initiated
        if station.call_handover_check():
            # allocate channel
            station.allocate_channel()

            # get index of next station depending on direction
            if event.direction == Direction.RIGHT:
                next_station = event.station + 1
            else:
                next_station = event.station - 1

            # remaining distance is the full distance of the base station range
            remaining_distance = 2
            # calculate time to next station
            time_to_next_station = (remaining_distance / event.speed) * 3600

            # if time to next station is greater than call duration, create call termination event, call is terminated. if next station is less than 0 or greater than 19, call is terminated. else call is handed over to next station
            if time_to_next_station > event.duration:
                #create call termination event
                new_event = Call_termination(self.current_time + event.duration, event.station)
            
            elif next_station < 0 or next_station > 19:
                #create call termination event
                new_event = Call_termination(self.current_time + time_to_next_station, event.station)
            else:
                #create call handover event
                new_event = Call_handover(self.current_time + time_to_next_station, event.station, event.duration - time_to_next_station, event.speed, event.direction)

            # insert new event in future events list
            self.insert_event(new_event)

        # if call cannot be initiated and event time is after the warmup period, call is dropped
        elif self.current_time > self.warmup_period:
            self.dropped_calls += 1

    # function to read events from future events list and handle them
    def handle_events(self):
        # pop first event
        event = self.future_events.pop(0)
        # set current time to event time
        self.current_time = event.time

        # handle event
        if event.type == Event_type.CALL_INITIATION:
            self.handle_call_initiation(event)
            # increment generated calls
            self.generated_calls += 1
        elif event.type == Event_type.CALL_TERMINATION:
            self.handle_call_termination(event)
        elif event.type == Event_type.CALL_HANDOVER:
            self.handle_call_handover(event)

    def end_simulation(self):
        return len(self.future_events) == 0 or self.generated_calls== self.total_calls

    # create new calls for the simulation and insert them in future events list
    def generate_new_calls(self):
        for i in range(self.total_calls - 1):
            # create new call initiation event
            new_event = Call_initiation(self.current_time + get_random_interarrival(), get_random_base_station(), get_random_duration(), get_random_speed(), get_random_position(), get_random_direction())

            # update current time
            self.current_time = new_event.time

            # append new event to future event list
            self.future_events.append(new_event)