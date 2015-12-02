# Jade Huang
# baseline PD predictor
# based on average of passing networks in group stage

import os
import re
from collections import defaultdict

# allPasses[team][p1-p2] = totalPasses
allPasses = defaultdict(lambda: defaultdict(int))

matchdays = ["matchday" + str(i) for i in xrange(1, 7)]
for matchday in matchdays:
    path = matchday + "/networks/"
    for network in os.listdir(path):
        if re.search("-edges", network):
            edgeFile = open(path + network, "r")

            teamName = re.sub("[^-]*-", "", network, count=1)
            teamName = re.sub("-edges", "", teamName)
            teamName = re.sub("_", " ", teamName)
            for line in edgeFile:
                line = line.rstrip().split("\t")
                p1, p2, weight = line
                p_key = p1 + "-" + p2
                allPasses[teamName][p_key] += int(weight)
                print "%s, %s, %s" % (teamName, p_key, weight)

# normalize over 6 matchdays
for teamName in allPasses:
    for p_key in allPasses[teamName]:
        allPasses[teamName][p_key] /= 6

# for round of 16, store which teams made it
# compare with both games to see how accurate
# the average of all group games is


