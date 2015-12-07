#i Jade Huang
# baseline PD predictor
# given two teams, output the average of past passing networks
# when these two teams played during the group stage
# in the 2014-15 season

# TODO: issue is that if teamA plays teamB in round of 16,
# they probably/most likely/definitely don't play
# each other during group stage.
#
# to use this baseline idea, would have to use 2015-16
# season. So putting this on hold.

import os
import re
from collections import defaultdict

matches = defaultdict(str)
matchesByTeam = defaultdict(str)
groupMatches = defaultdict(str)

def getTeamNameFromFile(network):
    teamName = re.sub("[^-]*-", "", network, count=1)
    teamName = re.sub("-edges", "", teamName)
    teamName = re.sub("_", " ", teamName)
    return teamName

def getMatchIDFromFile(network):
    matchID = re.sub("_.*", "", network)
    return matchID

def getOppTeam(matchID, teamName):
    team1, team2 = groupMatches[matchID].rsplit("-", 1)
    if team1 == teamName:
        return team2
    else: return team1

# for round of 16, store which teams made it
# compare with both games to see how accurate
# the average of all group games is

# store which teams faced each other
# by matching matchID


rpath = "r-16/networks/"
r16Teams = []
scorePerTeam1 = defaultdict(float)
scorePerTeam2 = defaultdict(float)
allR16Passes = defaultdict(lambda: defaultdict(int))

for network in os.listdir(rpath):
    if re.search("-edges", network):
        edgeFile = open(rpath + network, "r")
        teamName = getTeamNameFromFile(network)
        matchID = getMatchIDFromFile(network)

        # store which teams played each other
        m = matches[matchID]
        if m == "":
            matches[matchID] = teamName
        else:
            matchesByTeam[teamName] = matches[matchID]
            matchesByTeam[matches[matchID]] = teamName
            matches[matchID] += "-" + teamName

        # handle two games
        if teamName not in r16Teams:
            r16Teams.append(teamName)
        for line in edgeFile:
            line = line.rstrip().split("\t")
            p1, p2, weight = line
            p_key = p1 + "-" + p2
            t_key = matchID + "-" + teamName
            allR16Passes[t_key][p_key] += int(weight)

print r16Teams
for matchID in matches:
    print "%s: %s" % (matchID, matches[matchID])

for team in matchesByTeam:
    print "%s, %s" % (team, matchesByTeam[team])

# allGroupPasses[team][p1-p2] = totalPasses
allGroupPasses = defaultdict(lambda: defaultdict(int))
timesPlayed = defaultdict(int)

matchdays = ["matchday" + str(i) for i in xrange(1, 7)]
for matchday in matchdays:
    path = matchday + "/networks/"
    # first pass: figure out which teams played each other
    for network in os.listdir(path):
        if re.search("-edges", network):
            teamName = getTeamNameFromFile(network)
            matchID = getMatchIDFromFile(network)
            m = groupMatches[matchID]
            if m == "":
                groupMatches[matchID] = teamName
            else:
                groupMatches[matchID] += "-" + teamName

    # TODO: this could be more efficient
    # second pass, only accumulate counts for team pairs
    # that appeared in round of 16
    for network in os.listdir(path):
        if re.search("-edges", network):
            teamName = getTeamNameFromFile(network)
            if teamName not in r16Teams:
                continue
            edgeFile = open(path + network, "r")
            # check to make sure the opponent played is 
            # the same as r16 opponent
            matchID = getMatchIDFromFile(network)
            oppTeamName = getOppTeam(matchID, teamName) 
            # if opposing team wasn't in round of 16
            if oppTeamName not in r16Teams:
                continue
            print "matchesByTeam[%s] = %s" % (teamName,
                    matchesByTeam[teamName])
            print "matchesByTeam[%s] = %s" % (oppTeamName,
                    matchesByTeam[oppTeamName])

            # if opposing team wasn't the same as the one
            # that was faced in round of 16
            if matchesByTeam[teamName] == oppTeamName \
                    or matchesByTeam[oppTeamName] == teamName:
                print "yey"
                # TODO: not going to play same team
                # during group stage as in round of 16
                #
                t_key = teamName + "-" + oppTeamName

                for line in edgeFile:
                    line = line.rstrip().split("\t")
                    p1, p2, weight = line
                    p_key = p1 + "-" + p2
                    allGroupPasses[t_key][p_key] += int(weight)
                timesPlayed[t_key] += 1
                print "%s, %s, %s" % (teamName, p_key, weight)

# normalize over times played (not necessarily 6)
for teamName in allGroupPasses:
    for p_key in allGroupPasses[teamName]:
        norm = timesPlayed[teamName]
        print "%s played %s times" % (teamName, norm)
        allGroupPasses[teamName][p_key] /= norm

for matchID in matches:
    print matchID, matches[matchID]
    teams = matches[matchID]

    # for each pairing, look at passing dist from group stage
    # take average
    # compare to both r-16 games
    groupPasses = allGroupPasses[teams]
    for matchTeam in allR16Passes:
        matchID, team = matchTeam.split("-")
        for players in allR16Passes[matchTeam]:
            pred = allGroupPasses[teams][players]
            targ = allR16Passes[team][players]
            # print "pred: %s vs. targ: %s" % (pred, targ)
            scorePerTeam1[teams] += targ - pred


for teamName in allPasses:
    for p_key in allPasses[teamName]:
        weight = allPasses[teamName][p_key]
        # print "%s, %s, %s" % (teamName, p_key, weight)
#
#
# avgScorePerTeam = defaultdict(float)
# print "Scores for first game in Round of 16:"
# print "-------------------------------------"
# print "Team\t\t\tScore"
# print "----\t\t\t-----"
# for team in scorePerTeam1:
#     avgScorePerTeam[team] += scorePerTeam1[team]
#     print("{0:23}\t{1:0.4f}".format(team, scorePerTeam1[team]))
#
# print ""
# print "Scores for second game in Round of 16:"
# print "-------------------------------------"
# print "Team\t\t\tScore"
# print "----\t\t\t-----"
# for team in scorePerTeam2:
#     avgScorePerTeam[team] += scorePerTeam2[team]
#     print("{0:23}\t{1:0.4f}".format(team, scorePerTeam2[team]))
#
# # calculate average score per team
# for team in avgScorePerTeam:
#     avgScorePerTeam[team] /= 2
#
# print ""
# print "Average Scores for Round of 16:"
# print "-------------------------------------"
# print "Team\t\t\tScore"
# print "----\t\t\t-----"
# for team in avgScorePerTeam:
#     print("{0:23}\t{1:0.4f}".format(team, avgScorePerTeam[team]))
#
# # calculate average score overall
# sumScore = sum([avgScorePerTeam[team] for team in avgScorePerTeam])
# sumScore /= 16
# print ""
# print "Average Score Overall: %.4f" % sumScore
