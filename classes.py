import collections
from collections import defaultdict
import os
import re
from snap import *


def getMatchIDFromFile(network):
	matchID = re.sub("_.*", "", network)
	return matchID

def getTeamNameFromNetwork(network):
	teamName = re.sub("[^-]*-", "", network, count=1)
	teamName = re.sub("-edges", "", teamName)
	teamName = re.sub("_", " ", teamName)
	return teamName

class CountAvgPassesFeature():
	def __init__(self, count_file_name):
		self.avgCounts = defaultdict(lambda: defaultdict(float))
		count_file = open(count_file_name, "r")
		for line in count_file:
			team, players, weight = line.strip().split(", ")
			self.avgCounts[team][players] = weight

	def getCount(self, team, player1, player2):
		p_key = player1 + "-" + player2
		return self.avgCounts[team][p_key]

class PlayerPositionFeature():
	def __init__(self, squad_dir):

		def getTeamNameFromFile(teamFile):
			teamName = re.sub("-squad.*", "", teamFile)
			teamName = re.sub("_", " ", teamName)
			return teamName

		self.teamNumName = defaultdict(lambda: defaultdict(str))
		self.teamNumPos = defaultdict(lambda: defaultdict(str))

		for team in os.listdir(squad_dir):
			if re.search("-squad", team):
				path = squad_dir + team
				teamFile = open(squad_dir + team, "r")
				teamName = getTeamNameFromFile(team)
				for player in teamFile:
					num, name, pos = player.rstrip().split(", ")
					self.teamNumName[teamName][num] = name
					self.teamNumPos[teamName][num] = pos

	def getPos(self, teamName, num):
		return self.teamNumPos[teamName][num]

	def getName(self, teamName, num):
		return self.teamNumName[teamName][num]

	def isSamePos(self, teamName, num1, num2):
		ret = 1
		if self.getPos(teamName, num1) != self.getPos(teamName, num2):
			ret = 0
		return ret

class RankingFeature():
	def __init__(self, rankFileName):
		self.rankings = defaultdict(int)
		rank_file = open(rankFileName, "r")
		for rank in rank_file:
			rank, team = rank.rstrip().split(", ")
			self.rankings[team] = int(rank)

	def getRank(self, team):
		return self.rankings[team]

	def isHigherInRank(self, team1, team2):
		return self.getRank(team1) > self.getRank(team2)

	def getDiffInRank(self, team1, team2):
		return self.getRank(team1) - self.getRank(team2)

# unsuccessful feature
class MeanDegreeFeature():

	def __init__(self):
		folder = "passing_distributions/2014-15/"
		allGames = ["matchday" + str(i) for i in xrange(1, 7)]
		allGames.append("r-16")
		allGames.append("q-finals")
		allGames.append("s-finals")

		self.meanDegree = defaultdict(lambda: defaultdict(float))

		for matchday in allGames:
			path = folder + matchday + "/networks/"
			for network in os.listdir(path):
				if re.search("-edges", network):
					edgeFile = open(path + network, "r")

					degreePerPlayer = defaultdict(int)
					teamName = getTeamNameFromNetwork(network)
					matchID = getMatchIDFromFile(network)
					# print "team: %s" % teamName
					totalDegree = 0

					for players in edgeFile:
						p1, p2, weight = players.rstrip().split("\t")
						# print "p1: %s, p2: %s, weight: %f" % (p1, p2, float(weight))
						degreePerPlayer[p1] += 1

					# count number of nodes to take average over team
					nodeFile = open(path + matchID + "_tpd-" + re.sub(" ", "_", teamName) + "-nodes", "r")
					players = [line.rstrip() for line in nodeFile]
					numPlayers = len(players)
					totalDegree = 0
					for player in degreePerPlayer:
						totalDegree += degreePerPlayer[player]

					avgDegree = totalDegree / numPlayers
					# print "Avg degree for %s is %f" % (teamName, avgDegree)
					self.meanDegree[matchID][teamName] = avgDegree
	
	def getMeanDegree(self, matchID, teamName):
		return self.meanDegree[matchID][teamName]

# Returns the average betweenness centrality of each player
# calculated only using group stage, like average degree
class BetweennessFeature():
	def __init__(self):
		folder = "passing_distributions/2014-15/"
		allGames = ["matchday" + str(i) for i in xrange(1, 7)]
		# allGames.append("r-16")
		# allGames.append("q-finals")
		# allGames.append("s-finals")

		self.betweenCentr = defaultdict(lambda: defaultdict(float))

		for matchday in allGames:
			path = folder + matchday + "/networks/"
			for network in os.listdir(path):
				if re.search("-edges", network):
					edgeFile = open(path + network, "r")

					degreePerPlayer = defaultdict(int)
					teamName = getTeamNameFromNetwork(network)
					matchID = getMatchIDFromFile(network)

					edges = [line.rstrip() for line in edgeFile]

					nodeFile = open(path + matchID + "_tpd-" + re.sub(" ", "_", teamName) + "-nodes", "r")
					players = [line.rstrip() for line in nodeFile]
					
					# build each network

					PlayerGraph = TUNGraph.New()
					for player in players:
						num, name = player.split("\t")
						PlayerGraph.AddNode(int(num))
					for edge in edges:
						src, dest, weight = edge.split("\t")
						src = int(src)
						dest = int(dest)
						PlayerGraph.AddEdge(src, dest)

					# calculate betweenness
					Nodes = TIntFltH()
					Edges = TIntPrFltH()
					GetBetweennessCentr(PlayerGraph, Nodes, Edges, 1.0)

					players_by_between = [(node, Nodes[node]) for node in Nodes]
					for player in players_by_between:
						num, betw = player
						self.betweenCentr[teamName][num] += betw

		# normalize over number of matchdays
		for teamName in self.betweenCentr:
			for num in self.betweenCentr[teamName]:
				self.betweenCentr[teamName][num] /= 6

	def getBetweenCentr(self, matchID, teamName, player):
		return self.betweenCentr[teamName][int(player)]

# average passes completed and attempted per player feature
# averaged over all group games
class PassesComplAttempPerPlayerFeature():
	def __init__(self):
		folder = "passing_distributions/2014-15/"
		allGames = ["matchday" + str(i) for i in xrange(1, 7)]
		# allGames.append("r-16")
		# allGames.append("q-finals")
		# allGames.append("s-finals")

		self.pcPerPlayer = defaultdict(lambda: defaultdict(float))
		self.paPerPlayer = defaultdict(lambda: defaultdict(float))
		self.pcPercPerPlayer = defaultdict(lambda: defaultdict(float))

		for matchday in allGames:
			path = folder + matchday + "/networks/"
			for network in os.listdir(path):
				if "+" not in network:
					if re.search("-players", network):
						playerFile = open(path + network, "r")

						teamName = getTeamNameFromNetwork(network)
						matchID = getMatchIDFromFile(network)

						players = [line.rstrip() for line in playerFile]
						print "matchID is", matchID
						for player in players:
							print player
							num, pc, pa, percPc = player.split(",")
							self.pcPerPlayer[teamName][num] += float(pc) / 6.0
							self.paPerPlayer[teamName][num] += float(pa) / 6.0
							self.pcPercPerPlayer[teamName][num] += float(percPc) / 6.0

	def getPC(self, teamName, num):
		return self.pcPerPlayer[teamName][num]

	def getPA(self, teamName, num):
		return self.pcPerPlayer[teamName][num]

	def getPCPerc(self, teamName, num):
		return self.pcPercPerPlayer[teamName][num]



