from statistics import mean
from simulation_model import Simulator
import numpy as np
import scipy.stats as stats
import pandas as pd

blocked_calls_qos = 2
dropped_calls_qos = 1
# function to run simulation, inputs: epochs, num_iter, scheme, total_calls, warmup_period
def run_simulation(epochs, num_iter, scheme, total_calls, warmup_period):
    avg_blocked_rate = []
    avg_dropped_rate = []
    qos_achieved_count = 0
    qos_failed_blocked_count = 0
    qos_failed_dropped_count = 0
    num_sims = 0
    records = []
    for i in range(epochs):
        blocked_rates_ls = []
        dropped_rates_ls = []
        for j in range(num_iter):
            # create simulator
            sim = Simulator(scheme, total_calls, warmup_period)

            # generate new calls for warmup period
            sim.generate_new_calls()

            # handle events
            while not sim.end_simulation():
                sim.handle_events()
            
            # calculate percentage blocked and dropped calls to  and append to list
            blocked_rate = sim.blocked_calls / sim.new_calls *100
            dropped_rate = sim.dropped_calls / sim.new_calls *100
            blocked_rates_ls.append(blocked_rate)
            dropped_rates_ls.append(dropped_rate)

            # check if QoS is achieved, if it is increment qos_achieved_count, else increment qos_failed_count
            if blocked_rate <= blocked_calls_qos and dropped_rate <= dropped_calls_qos:
                qos_achieved_count += 1
            if blocked_rate > blocked_calls_qos:
                qos_failed_blocked_count += 1
            if dropped_rate > dropped_calls_qos:
                qos_failed_dropped_count += 1
                
            # increment num_sims
            num_sims += 1
            
        # calculate average blocked and dropped rates and append to list
        avg_blocked_rate.append(np.mean(blocked_rates_ls))
        avg_dropped_rate.append(np.mean(dropped_rates_ls))

        # print epoch number and average blocked and dropped rates to 3 decimal places
        print("Epoch: " + str(i+1) + " Avg Blocked Rate: " + str(round(np.mean(blocked_rates_ls), 5)) + "% Avg Dropped Rate: " + str(round(np.mean(dropped_rates_ls), 5)) + "%")

    # print divider
    print("-" * 50)
    # print QoS achieved count, QoS failed blocked count, QoS failed dropped count, and number of simulations
    print("Number of Simulations: " + str(num_sims))
    print("QoS Achieved Count: " + str(qos_achieved_count))
    print("QoS Failed due to Call Blocked rate: " + str(qos_failed_blocked_count))
    print("QoS Failed due to Call Dropped rate: " + str(qos_failed_dropped_count))

    # calculate mean and standard deviation of blocked and dropped rates
    mean_blocked = np.mean(avg_blocked_rate)
    std_blocked = np.std(avg_blocked_rate)
    mean_dropped = np.mean(avg_dropped_rate)
    std_dropped = np.std(avg_dropped_rate)

    # calculate confidence intervals with 95% confidence with stats
    conf_int_blocked = stats.t.interval(0.95, len(avg_blocked_rate)-1, loc=mean_blocked, scale=std_blocked/np.sqrt(len(avg_blocked_rate)))
    conf_int_dropped = stats.t.interval(0.95, len(avg_dropped_rate)-1, loc=mean_dropped, scale=std_dropped/np.sqrt(len(avg_dropped_rate)))

    # print statistics divider
    print("-" * 50)
    # print mean, deviation, and confidence intervals of blocked rates separated by newline
    print("Blocked Rate:")
    print("Mean: " + str(round(mean_blocked, 5)) + "%")
    print("Standard Deviation: " + str(round(std_blocked, 5)) + "%")
    print("95% Confidence Interval: (" + str(round(conf_int_blocked[0], 5)) + ", " + str(round(conf_int_blocked[1], 5)) + ")")
    # print mean, deviation, and confidence intervals of dropped rates separated by newline
    print("Dropped Rate:")
    print("Mean: " + str(round(mean_dropped, 5)) + "%")
    print("Standard Deviation: " + str(round(std_dropped, 5)) + "%")
    print("95% Confidence Interval: (" + str(round(conf_int_dropped[0], 5)) + ", " + str(round(conf_int_dropped[1], 5)) + ")")

    return [mean_blocked, mean_dropped]
    # return records