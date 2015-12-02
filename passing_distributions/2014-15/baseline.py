#i Jade Huang
# baseline PD predictor
# based on average of passing networks in group stage
# for 2014-15 season

import os
import re
from collections import defaultdict

def getTeamNameFromFile(network):
    teamName = re.sub("[^-]*-", "", network, count=1)
    teamName = re.sub("-edges", "", teamName)
    teamName = re.sub("_", " ", teamName)
    return teamName

# allGroupPasses[team][p1-p2] = totalPasses
allGroupPasses = defaultdict(lambda: defaultdict(int))

matchdays = ["matchday" + str(i) for i in xrange(1, 7)]
for matchday in matchdays:
    path = matchday + "/networks/"
    for network in os.listdir(path):
        if re.search("-edges", network):
            edgeFile = open(path + network, "r")
            teamName = getTeamNameFromFile(network)

            for line in edgeFile:
                line = line.rstrip().split("\t")
                p1, p2, weight = line
                p_key = p1 + "-" + p2
                allGroupPasses[teamName][p_key] += int(weight)
                # print "%s, %s, %s" % (teamName, p_key, weight)

# normalize over 6 matchdays
for teamName in allGroupPasses:
    for p_key in allGroupPasses[teamName]:
        allGroupPasses[teamName][p_key] /= 6

# for round of 16, store which teams made it
# compare with both games to see how accurate
# the average of all group games is

# output score per team

rpath = "r-16/networks/"
r16Teams = []
scorePerTeam1 = defaultdict(float)
scorePerTeam2 = defaultdict(float)

for network in os.listdir(rpath):
    if re.search("-edges", network):
        totalPasses = 0
        edgeFile = open(rpath + network, "r")
        teamName = getTeamNameFromFile(network)
        scorePerTeam = scorePerTeam1
        if teamName in r16Teams:
            scorePerTeam = scorePerTeam2
        else:
            r16Teams.append(teamName)
        for line in edgeFile:
            line = line.rstrip().split("\t")
            p1, p2, weight = line
            p_key = p1 + "-" + p2
            if p_key in allGroupPasses[teamName]:
                # evaluate
                est = allGroupPasses[teamName][p_key]
                scorePerTeam[teamName] += int(weight) - est
            totalPasses += 1
        # normalize by total passes
        scorePerTeam[teamName] /= totalPasses

avgScorePerTeam = defaultdict(float)
print "Scores for first game in Round of 16:"
print "-------------------------------------"
print "Team\t\t\tScore"
print "----\t\t\t-----"
for team in scorePerTeam1:
    avgScorePerTeam[team] += scorePerTeam1[team]
    print("{0:23}\t{1:0.4f}".format(team, scorePerTeam1[team]))

print ""
print "Scores for second game in Round of 16:"
print "-------------------------------------"
print "Team\t\t\tScore"
print "----\t\t\t-----"
for team in scorePerTeam2:
    avgScorePerTeam[team] += scorePerTeam2[team]
    print("{0:23}\t{1:0.4f}".format(team, scorePerTeam2[team]))

# calculate average score per team
for team in avgScorePerTeam:
    avgScorePerTeam[team] /= 2

print ""
print "Average Scores for Round of 16:"
print "-------------------------------------"
print "Team\t\t\tScore"
print "----\t\t\t-----"
for team in avgScorePerTeam:
    print("{0:23}\t{1:0.4f}".format(team, avgScorePerTeam[team]))

# calculate average score overall
sumScore = sum([avgScorePerTeam[team] for team in avgScorePerTeam])
sumScore /= 16
print ""
print "Average Score Overall: %.4f" % sumScore
