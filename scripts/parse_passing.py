# Jade Huang
# Parse passing distributions (PD)
# Assumes PD is in .csv format
# usage: python parse_passing.py -i INFILE -o OUTFILE
#        where INFILE is a .csv file with passing distributions
#        OUTFILE will be the prefix for two edge/node lists
#        (one per team)

import sys
import re
import argparse
from collections import defaultdict

parser = argparse.ArgumentParser(description='Process some passing \
distributions')
parser.add_argument('-in', '-i', dest='infile', required = True)
parser.add_argument('-out', '-o', dest='outfile', required = True)
parsed_args = parser.parse_args()

infile = open(parsed_args.infile, 'r')
passing_dist = [line for line in infile]

# player number -> player name
num_to_name = defaultdict(str)

# player1 -> player2 = weight
passing_edges = defaultdict(lambda: defaultdict(str))

# player number -> time played
num_to_time = defaultdict(float)

# index in array -> player number
index_to_num = defaultdict(str)

# index in array -> player passing stats
index_to_stats = defaultdict(str)

# player[index] = [stat value, stat value, etc.]
player_stats = defaultdict(list)

# player number -> total passes received
total_passes_received_by_player = defaultdict(float)

# stat index -> total stats
total_passes_received_by_stats = defaultdict(str)

def init():
    global num_to_name
    global passing_edges
    global num_to_time
    global index_to_num
    global index_to_stats
    global player_stats
    global total_passes_received_by_player
    global total_passes_received_by_stats

    num_to_name = defaultdict(str)
    passing_edges = defaultdict(lambda: defaultdict(str))
    num_to_time = defaultdict(float)
    index_to_num = defaultdict(str)
    index_to_stats = defaultdict(str)
    player_stats = defaultdict(list)
    total_passes_received_by_player = defaultdict(float)
    total_passes_received_by_stats = defaultdict(str)

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
        for index in xrange(14):
            index_to_num[index] = line[index]
        for index in xrange(14, len(line)):
            index_to_stats[index] = line[index]

def store_edges(start, end):
    # store edges
    for line in passing_dist[start:end]:
        split = line.rstrip().split(",")
        if "Total passes received" not in split[0]:
            # first store num -> name
            name, num, time = split[0:3]
            if num == '': # in case Excel parsing messed up
                num = re.search('[0-9]+', split[0]).group(0)
            name = re.sub('[0-9]+', "", name)
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
                    passing_edges[num][player2] = split[index]
                    # print "%s -> %s: %s" % (num, player2, split[index])

            # store player stats
            # strip percentage sign of last stat & make into decimal
            perc = split[len(split) - 1][:-1]
            split[len(split) - 1] = "0.%s" % str(perc)
            player_stats[num] = split[14:]
            # print "player_stats[%s] = "% num, split[14:]
        else:
            # players
            total_passes = split[3:17]
            for index in xrange(14):
                player = index_to_num[index]
                total_passes_received_by_player[player] = total_passes[index]
                # print "%s -> %s" % (player, total_passes[index])

            # stats
            total_stats = split[17:]
            # pre-process
            total_stats_processed = []
            for stat in total_stats:
                if " " in stat:
                    # split
                    stat = stat.split()
                    total_stats_processed += stat
                elif len(stat) == 0:
                    # remove empty spots
                    continue
                elif "%" in stat:
                    stat = stat[:-1]
                    stat = "0." + stat
                    total_stats_processed.append(stat)
                else:
                    total_stats_processed.append(stat)

            offset = 17
            for index in xrange(len(total_stats_processed)):
                total_passes_received_by_stats[index+offset] = total_stats_processed[index]

# get team names
teams_orig = passing_dist[3].rstrip().split(",")
teams = []
for t in teams_orig:
    if t != "": teams.append(t)
team1 = teams[0]
team2 = teams[2]

# team 1
outfile = open(parsed_args.outfile + "-" + team1 + "-edges", 'w')
init()
setup(6, 7)
store_edges(7, 22)
# print edges
for player1 in passing_edges:
    for player2 in passing_edges[player1]:
        outfile.write("%s\t%s\t%s\n" % (player1, player2, \
                passing_edges[player1][player2]))
# print player num to player names
num_name_outfile = open(parsed_args.outfile + "-" + team1 + "-nodes", 'w')
for num in num_to_name:
    num_name_outfile.write("%s\t%s\n" % (num, num_to_name[num]))

# team 2
outfile = open(parsed_args.outfile + "-" + team2 + "-edges", 'w')
init()
setup(24, 25)
store_edges(25, 40)
# print edges
for player1 in passing_edges:
    for player2 in passing_edges[player1]:
        outfile.write("%s\t%s\t%s\n" % (player1, player2, \
                passing_edges[player1][player2]))
# print player num to player names
num_name_outfile = open(parsed_args.outfile + "-" + team2 + "-nodes", 'w')
for num in num_to_name:
    num_name_outfile.write("%s\t%s\n" % (num, num_to_name[num]))
