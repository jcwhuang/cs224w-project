# Jade Huang
# Parse passing distributions
# Assumes PD is in .csv format
# usage: python parse_passing.py < pd.csv

import sys
import re
from collections import defaultdict

passing_dist = sys.stdin.readlines()
# player number -> player name
num_to_name = defaultdict(str)

# player1 -> player2 = weight
passing_edges = defaultdict(str)

# player number -> time played
num_to_time = defaultdict(float)

# index in array -> player number
index_to_num = defaultdict(str)

# index in array -> player passing stats
index_to_stats = defaultdict(str)

# player[index] = [stat value, stat value, etc.]
player_stats = defaultdict(list)

def setup(start, end):
    # setup
    for line in passing_dist[start:end]:
        # strip off beginning labels
        line = line.rstrip().split(",")[3:]

        # adding more descriptive labels
        line[14] += "-long"
        line[15] += "-long"
        line[16] += "-med"
        line[17] += "-med"
        line[18] += "-short"
        line[19] += "-short"
        line[20] += "-total"
        line[21] += "-total"
        line[22] += "-success"

        # making index -> num/stats dicts
        offset = 3
        for index in xrange(14):
            index_to_num[index+offset] = line[index]
        for index in xrange(14, len(line)):
            index_to_stats[index+offset] = line[index]

def store_edges(start, end):
    # store edges
    for line in passing_dist[start:end]:
        split = line.rstrip().split(",")
        print split
        if "Total passes received" not in split[0]:
            # first store num -> name
            name, num, time = split[0:3]
            num_to_name[num] = name

            # convert time to float
            time = re.sub("\"", "", time)
            hour, mins = time.split("\'")
            hour = float(hour)
            mins = float(mins) / 60
            num_to_time[num] = hour + mins
            split = split[3:]

            # store passing edges
            for index in xrange(14):
                if split[index] != '' and split[index] != '-':
                    player2 = index_to_num[index]
                    print "%s -> %s: %s" % (num, player2, split[index])

            # store player stats
            # strip percentage sign of last stat & make into decimal
            perc = split[len(split) - 1][:-1]
            split[len(split) - 1] = "0.%s" % str(perc)
            player_stats[num] = split[14:]
            print "player_stats[%s] = "% num, split[14:]
        # TODO: deal with Total passes received


setup(6, 7)
store_edges(7, 22)
# TODO: deal with storing/printing stats for both teams
