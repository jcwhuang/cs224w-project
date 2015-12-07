import collections, util, math, random
import classes, scoring
import copy
import os
import glob
import re
from collections import defaultdict
import unicodedata
import random

class PredictPD():

	def __init__(self):

		# Feature: Specific pass count per match
		# This is kind of weird because it's like rote memorization
		# TODO: think more about this
		# countSpecFile = "spec_passes_count.txt"
		# countSpecificPassesFeature = classes.countSpecificPassesFeature(countSpecFile)
	
		self.weights = defaultdict(int)
		# self.weights["avgPasses"] = 0
		# self.weights["isSamePos"] = 0
		# self.weights["isDiffPos"] = 0
		# self.weights["diffInRank"] = 0
		# # self.weights["wonAgainstSimTeam"] = 0
		# # self.weights["avgPassesPerPos"] = 0
		# self.weights["avgPassVol"] = 0
		# self.weights["avgPassPerc"] = 0

		self.stepSize = 0.01

		self.matchdays = ["matchday" + str(i) for i in xrange(1, 7)]

		self.folder = "passing_distributions/2014-15/"

		# Feature: Average pass count over group stage
		countAvgFile = "avg_passes_count.txt"
		self.countAvgPassesFeature = classes.CountAvgPassesFeature(countAvgFile)

		squad_dir = "squads/2014-15/squad_list/"
		self.playerPosFeature = classes.PlayerPositionFeature(squad_dir)

		rankFile = "rankings/2013_14_rankings.txt"
		self.rankFeature = classes.RankingFeature(rankFile)

		self.matches = defaultdict(str)

		self.totalPassesBetweenPos = defaultdict(lambda: defaultdict(int))
		self.totalPassesBetweenPlayers = defaultdict(lambda: defaultdict(int))
		self.totalPasses = defaultdict(int)

		self.teamNumToPos = defaultdict(lambda: defaultdict(str))
		self.initTeamNumToPos(squad_dir)

		self.passVolPerTeam = defaultdict(int)
		self.passPercPerTeam = defaultdict(float)

		self.teamStatsByMatch = defaultdict(lambda: defaultdict(list))

	# Average pairwise error over all players in a team
	# given prediction and gold
	def evaluate(self, features, weight):
		score = self.computeScore(features, self.weights)
		# print "score %f vs. actual %f" % (float(score), float(weight))
		loss = self.computeLoss(features, self.weights, float(weight))
		# print "Loss: %f" % loss
		return (score, loss)

	def computeLoss(self, features, weights, label):
		return (self.computeScore(features, weights) - label)**2

	# score is dot product of features & weights
	def computeScore(self, features, weights):
		score = 0.0
		for v in features:
			score += float(features[v]) * float(weights[v])
		return score

	# returns a vector
	# 2 * (phi(x) dot w - y) * phi(x)
	def computeGradientLoss(self, features, weights, label):
		scalar =  2 * self.computeScore(features, weights) - label
		mult = copy.deepcopy(features)
		for f in mult:
			mult[f] = float(mult[f])
			mult[f] *= scalar
		return mult

	# use SGD to update weights
	def updateWeights(self, features, weights, label):
		grad = self.computeGradientLoss(features, weights, label)
		for w in self.weights:
			self.weights[w] -= self.stepSize * grad[w]
			# print "updated weights[%s] = %f" % (w, self.weights[w])

	def getTeamNameFromNetwork(self, network):
		teamName = re.sub("[^-]*-", "", network, count=1)
		teamName = re.sub("-edges", "", teamName)
		teamName = re.sub("_", " ", teamName)
		return teamName

	def getTeamNameFromFile(self, teamFile):
		teamName = re.sub("-squad.*", "", teamFile)
		teamName = re.sub("_", " ", teamName)
		return teamName

	def initTeamNumToPos(self, squad_dir):
		for team in os.listdir(squad_dir):
			if re.search("-squad", team):
				path = squad_dir + team
				teamFile = open(squad_dir + team, "r")
				teamName = self.getTeamNameFromFile(team)
				for player in teamFile:
					num, name, pos = player.rstrip().split(", ")
					self.teamNumToPos[teamName][num] = pos

	def getMatchIDFromFile(self, network):
		matchID = re.sub("_.*", "", network)
		return matchID

	def getOppTeam(self, matchID, teamName):
		team1, team2 = self.matches[matchID].split("/")
		if team1 == teamName:
			return team2
		else: return team1

	def getMatchday(self, matchID):
		matchID = int(matchID)
		if matchID <= 2014322:
			return 0
		elif matchID >=2014323 and matchID <= 2014338:
			return 1
		elif matchID >= 2014339 and matchID <= 2014354:
			return 2
		elif matchID > 2014354:
			return 3
		else:
			return 4

	def featureExtractor(self, teamName, p1, p2, matchID, matchNum, weight):

		avgPasses = self.countAvgPassesFeature.getCount(teamName, p1, p2)
		# p_key = p1 + "-" + p2
		# self.totalPassesBetweenPlayers[teamName][p_key] += float(weight)
		# totalPasses = self.totalPassesBetweenPlayers[teamName][p_key]
		# avgPasses = totalPasses / (matchNum + 1)

		isSamePos = self.playerPosFeature.isSamePos(teamName, p1, p2)
		isDiffPos = abs(1 - isSamePos)

		oppTeam = self.getOppTeam(matchID, teamName)
		diffInRank = self.rankFeature.isHigherInRank(teamName, oppTeam)

		features = defaultdict(float)
		features["avgPasses"] = avgPasses
		# features["isSamePos"] = isSamePos
		# features["isDiffPos"] = isDiffPos
		# features["diffInRank"] = diffInRank

		# pos1 = self.teamNumToPos[teamName][p1]
		# pos2 = self.teamNumToPos[teamName][p2]

		# # keep a running total of past passes between positions
		# # how about a running average...
		# p_key = pos1 + "-" + pos2
		# self.totalPassesBetweenPos[teamName][p_key] += int(weight)
		# self.totalPasses[teamName] += int(weight)
		# # print "totalPassesBetweenPos[%s][%s] = %s" % (teamName, p_key, self.totalPassesBetweenPos[teamName][p_key])
		# # print "totalPasses[%s] = %s" % (teamName, self.totalPasses[teamName])
		# avgPassesPerPos = self.totalPassesBetweenPos[teamName][p_key] / float(self.totalPasses[teamName])
		# features["avgPassesPerPos"] = avgPassesPerPos

		# avgPassVol = self.passVolPerTeam[teamName] / (matchNum + 1.0)
		# avgPassPerc = self.passPercPerTeam[teamName] / (matchNum + 1.0)

		# oppAvgPassVol = self.passVolPerTeam[oppTeam] / (matchNum + 1.0)
		# oppAvgPassPerc = self.passPercPerTeam[oppTeam] / (matchNum + 1.0)

		# print "avgPassVol: %s vs oppAvgPassVol: %s" % (avgPassVol, oppAvgPassVol)
        
		# # TODO: test baseline on random
		# features["avgPassVol"] = 1 if avgPassVol > oppAvgPassVol else 0
		# features["avgPassPerc"] = 1 if avgPassPerc > oppAvgPassPerc else 0
  # #       #
		# for feature: won against a similar ranking team
		# 1. define history that we are able to use, i.e. previous games
		matchday = self.getMatchday(matchID)
		history = self.teamPlayedWith[teamName][:matchday]

		if len(history) > 0:
			def computeSim(rank1, rank2):
				return (rank1**2 + rank2**2)**0.5

			# 2. find most similar opponent in terms of rank
			# TODO: similarity could be defined better?
			oppTeamRank = self.rankFeature.getRank(oppTeam)
			simTeam = ""
			simTeamDistance = float('inf')
			rank1 = oppTeamRank
			for team in history:
				rank2 = self.rankFeature.getRank(team)
				sim = computeSim(rank1, rank2)
				if sim < simTeamDistance:
					simTeamDistance = sim
					simTeam = sim

			# 3. find out whether the game was won or lost
			# features["wonAgainstSimTeam"] = self.teamWonAgainst[teamName][matchday]

		return features

	def initMatches(self):
		# store match data for all 6 matchdays in group stage + r-16
		# match data including team + opponent team
		for matchday in self.matchdays + ["r-16"]:
			path = self.folder + matchday + "/networks/"
			for network in os.listdir(path):
				if re.search("-edges", network):
					edgeFile = open(path + network, "r")
					teamName = self.getTeamNameFromNetwork(network)
					matchID = self.getMatchIDFromFile(network)

					m = self.matches[matchID]
					if m == "":
						self.matches[matchID] = teamName
					else:
						self.matches[matchID] += "/" + teamName

		allScoresFilename = "matches4_groupStage_2014_15.txt"
		allScores = open(allScoresFilename, "r")
		self.matchesWithScores = [line.rstrip() for line in allScores]
		self.teamPlayedWith = defaultdict(list)
		self.teamWonAgainst = defaultdict(list)

		# for every team, store opponents in order by matchday
		for match in self.matchesWithScores:
			team1, score1, score2, team2 = match.split(", ")
			team1Won = 0
			if score1 > score2:
				team1Won = 1

			self.teamPlayedWith[team1].append(team2)
			self.teamPlayedWith[team2].append(team1)
			self.teamWonAgainst[team1].append(team1Won)
			self.teamWonAgainst[team2].append(abs(1 - team1Won))

	def initTeamStats(self):
		for matchday in self.matchdays:
			path = self.folder + matchday + "/networks/"
			# iterate over games
			for network in os.listdir(path):
				if re.search("-team", network):
					# store per match
					# or store per team?
					teamName = self.getTeamNameFromNetwork(network)
					teamName = re.sub("-team", "", teamName)
					matchID = self.getMatchIDFromFile(network)

					stats_file = open(path + network, "r")
					for line in stats_file:
						stats = line.rstrip().split(", ")
					
					self.teamStatsByMatch[teamName][matchID] = stats

	# Training
	# 	have features calculate numbers based on data
	# 	learn weights for features via supervised data (group stage games) and SGD/EM
	def train(self):
		# iterate over matchdays, predicting passes, performing SGD, etc.

		num_iter = 2
		self.initMatches()
		self.initTeamStats()
		
		pos = ["GK", "STR", "DEF", "MID"]
		allPosCombos = [pos1 + "-" + pos2 for pos1 in pos for pos2 in pos]

		for i in xrange(num_iter):
			avgLoss = 0
			totalEx = 0
			print "Iteration %s" % i
			print "------------"
			for w in self.weights:
					print "weights[%s] = %f" % (w, float(self.weights[w]))
			# iterate over matchdays -- hold out on some matchdays
			matchNum = 0

			# # try shuffling matchdays
			# random.shuffle(self.matchdays)


			allGames = []

			for matchday in self.matchdays:
				print "On " + matchday
				path = self.folder + matchday + "/networks/"
				# iterate over games
				for network in os.listdir(path):
					if re.search("-edges", network):
						# passesBetweenPos = defaultdict(lambda: defaultdict(int))
						allGames.append((path, network))


			# try shuffling games
			# random.shuffle(allGames)

			for game in allGames:
				path, network = game
				edgeFile = open(path + network, "r")

				teamName = self.getTeamNameFromNetwork(network)
				matchID = self.getMatchIDFromFile(network)
				# print "team: %s" % teamName
				for players in edgeFile:
					p1, p2, weight = players.rstrip().split("\t")
					# print "p1: %s, p2: %s, weight: %f" % (p1, p2, float(weight))

					teamFile = open(path + matchID + "_tpd-" + re.sub(" ", "_", teamName) + "-team", "r")
					for line in teamFile:
						stats = line.rstrip().split(", ")
					self.passVolPerTeam[teamName] += float(stats[0])
					self.passPercPerTeam[teamName] += float(stats[1])

					features = self.featureExtractor(teamName, p1, p2, matchID, matchNum, weight)

					# for f in features:
					# 	print "features[%s] = %f" % (f, float(features[f]))
					# for w in self.weights:
					# 	print "weights[%s] = %f" % (w, float(self.weights[w]))

					score, loss = self.evaluate(features, weight)
 					self.updateWeights(features, self.weights, int(weight))
 					avgLoss += loss
					totalEx += 1
				matchNum += 1
			print "Average loss: %f" % (avgLoss / totalEx)

	# Testing
	#	Predict, then compare with dev/test set (r-16 games)
	def test(self):
		# sum up average error

		print "Testing"
		print "-------"
		avgLoss = 0
		totalEx = 0
		matchNum = 0
		# for matchday in self.matchdays[4:]:
		matchday = "r-16"
		print "On " + matchday
		path = self.folder + matchday + "/networks/"
		# iterate over games
		for network in os.listdir(path):
			if re.search("-edges", network):
				edgeFile = open(path + network, "r")

				predEdgeFile = open("predicted/pred-" + network, "w+")

				teamName = self.getTeamNameFromNetwork(network)
				matchID = self.getMatchIDFromFile(network)
				print "team: %s" % teamName
				for players in edgeFile:
					p1, p2, weight = players.rstrip().split("\t")
					print "p1: %s, p2: %s, weight: %f" % (p1, p2, float(weight))

					features = self.featureExtractor(teamName, p1, p2, matchID, matchNum, weight)

					for f in features:
						print "features[%s] = %f" % (f, float(features[f]))
					for w in self.weights:
						print "weights[%s] = %f" % (w, float(self.weights[w]))

					score, loss = self.evaluate(features, weight)

					# print out predicted so can visually compare to actual
					predEdgeFile.write(p1 + "\t" + p2 + "\t" + str(score) + "\n")

					avgLoss += loss
					totalEx += 1
				matchNum += 1
		print "Average loss: %f" % (avgLoss / totalEx)

pred = PredictPD()
pred.train()
pred.test()
