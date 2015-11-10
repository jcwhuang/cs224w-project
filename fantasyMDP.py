import collections, util, math, random
import classes, scoring
import copy
import os

#to compute 15-man roster from available players
class ComputeRosterMDP(util.MDP):
	def __init__(self, players, budget):
		self.players=players
		self.budget=budget
		self.maxPositions = {'GK': 2, 'DEF': 5, 'MID': 5, 'STR': 3}

	# a state = (roster, budget, positions, teams)
	# roster -- a list of class Player that represents the players we have 
	#			chosen for our roster thus far
	# budget -- (int) how much money we have left to spend
	# positions -- a dict {"GK":num1; "DEF":num2; "MID":num3; "STR":num4}, where 
	#				num1 = number of goalkeepers on roster
	#				num2 = number of defenders on roster
	#				num3 = number of midfielders on roster
	#				num4 = number of forwardss on roster
	# teams -- dict: {classes.Team: int(number of players from that team on our roster)}
	#			(we can only choose up to 3 players from each Premier league
	#			team to put on our roster)
	def startState(self):
		teams = {}
		for t in AllTeams: #TO DO: make list of all teams in league
			teams[t] = 0
		positions = {}
		positions["GK"] = 0
		positions["DEF"] = 0
		positions["MID"] = 0
		positions["STR"] = 0
		return ([], self.budget, positions ,teams)

	#------------League Constraints on Roster--------------#
	# 1) 2 goalkeepers
	# 2) 5 defenders
	# 3) 5 midfielders
	# 4) 3 forwards
	# 5) budget = 100million
	# 6) Can select up to 3 players from a single Premier League team
	def actions(self,state):
		actions = []		
		for p in AllPlayers: #TO DO: create list of all players
			if p not in state[0]: #if not in roster yet
				positionConstraint = (state.positions[p.position] < self.maxPositions[p.position])
				budgetConstraint = (p.price < state.budget)
				teamConstraint = (state.teams[p.team] < 3)
				if positionConstraint and budgetConstraint and teamConstraint:
					actions.append(p)
		return actions
					
				
	def succAndProbReward(self, state, action):
		#if roster is full
		if len(state[0]) == 15:
			return []

		#compute new state
		newRoster = state[0]
		newRoster.append(action)
		newBudget = state[1]-action.price
		newPositions = state[2]
		newPosition[action.position] += 1
		newTeams = state[3]
		newTeams[action.team] += 1
		newState = (newRoster, newBudget, newPositions, newTeams)

		#TO DO: Reward function
		reward = 0 
		playedInGame = False 	# 1pt
		played60Min = False		# 2pt
		goalsScored = 0			# 6pt if GK or DEF, 5pt if MID, 4 if STR
		assists = 0				# 3pt
		noScoreOnGK = False		# 4pt if played 60min
		noScoreOnDEF = False	# 4pt if played 60min
		noScoreOnMID = False	# 1pt if played 60min
		penaltiesReceived = 0	# 1pt 
		penaltiesConceded = 0	# -1pt 
		penaltyMisses = 0		# -2pt
		penaltySaves = 0		# 5pt
		goalsConceded = 0		# -1pt/2goals for GK or MID
		yellowCard = False		# -1pt
		redCard = False			# -3pt
		savesByGK = 0			# 1pt/3saves
		recoveredBalls = 0		# 1pt/5balls



		return [(newState, 1, reward)]

	def discount(self):
		return 1



class ComputeMatchLineupMDP(util.MDP):
	def __init__(self, roster, budget):
		self.roster=roster
		self.budget=budget

	def startState(self):
		return ([],self.budget)

	def actions(self,state):
		return None

	def succAndProbReward(self, state, action):
		return None

#store all player data
players = {}
lines = [line.rstrip('\n') for line in open('fantasy_player_data/defenders')]
lines = lines + [line.rstrip('\n') for line in open('fantasy_player_data/forwards')]
lines = lines + [line.rstrip('\n') for line in open('fantasy_player_data/goalkeepers')]
lines = lines + [line.rstrip('\n') for line in open('fantasy_player_data/midfielders')]

#store basic player data
for line in lines:
	elems = line.split(",")
	p = classes.Player(elems[0], elems[1], elems[2], elems[3])
	players[elems[0]] = p

#store player match data
player_stat_features = {}
for i in os.listdir("player_statistics/2015-16/"):
	if  i.endswith(".py")==False and i.endswith("Store")==False:
		filename = "player_statistics/2015-16/" + i + "/csv/"
		for tf in os.listdir(filename):
			if tf.endswith("features"):
				if not player_stat_features.keys():
					ls = [line.rstrip('\n') for line in open(filename+tf)]
					#TO DO number: acronym, separated by tab
			elif tf.endswith("csv")==False and tf.endswith(".py")==False:
				#TO DO
				#iterating through a single match of player stats for one team
				#need to store player names to player number before doing this	
				continue

'''for p in players.keys():
	print players[p].name
	print players[p].team
	print players[p].position
	print players[p].price
'''

'''budget = 100.0
mdp = ComputeRosterMDP(players, budget)
rl = util.QLearningAlgorithm(mdp.actions, mdp.discount(), util.fantasyFeatureExtractor)
'''
