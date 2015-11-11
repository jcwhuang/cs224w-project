import collections, util, math, random
import classes, scoring
import copy
import os
import glob
import re
from collections import defaultdict
import unicodedata

# to compute 15-man roster from available players
class ComputeRosterMDP(util.MDP):
	def __init__(self, players, budget, allTeams, allPlayers):
		self.players=players
		self.budget=budget
		self.maxPositions = {'GK': 2, 'DEF': 5, 'MID': 5, 'STR': 3}
        # self.allTeams=allTeams
        # self.allPlayers = allPlayers

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
		teams = {t:0 for t in self.allTeams}
		positions = {pos:0 for pos in self.maxPositions}
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
		# TO DO: how to store all players? 
		#       There are duplicate names from different teams :(
		#       The alternative is to use the dict team->player name -> playernum
		for p in AllPlayers:
			if p not in state[0]: #if not in roster yet
				positionConstraint = (state.positions[p.position] < self.maxPositions[p.position])
				budgetConstraint = (p.price < state.budget)
				teamConstraint = (state.teams[p.team] < 3)
				if positionConstraint and budgetConstraint and teamConstraint:
					actions.append(p)
		return actions
					
				
	def succAndProbReward(self, state, action):
		# if roster is full
		if len(state[0]) == 15:
			return []

		# compute new state
		newRoster = state[0]
		newRoster.append(action)
		newBudget = state[1]-action.price
		newPositions = state[2]
		newPosition[action.position] += 1
		newTeams = state[3]
		newTeams[action.team] += 1
		newState = (newRoster, newBudget, newPositions, newTeams)

		# TO DO: Reward function
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

# list of all players as Players
allPlayers = {}

# for positions, only last names are included along with price, team, and position
lines = [line.rstrip('\n') for line in open('fantasy_player_data/positions/defenders')]
lines = lines + [line.rstrip('\n') for line in open('fantasy_player_data/positions/forwards')]
lines = lines + [line.rstrip('\n') for line in open('fantasy_player_data/positions/goalkeepers')]
lines = lines + [line.rstrip('\n') for line in open('fantasy_player_data/positions/midfielders')]

# compare ignoring accented characters
def check_for_accented_key(k, d):
	for key in d:
		u1 = unicodedata.normalize('NFC', k.decode('utf-8'))
		u2 = unicodedata.normalize('NFC', key.decode('utf-8'))
		if u1 == u2:
			return d[key]
	raise "Couldn't find team name"

# team_to_player_num[team][player_last_name] = player_num
team_to_player_num = defaultdict(lambda: defaultdict(str))

# team_to_player_name[team][player_num] = player_name
team_to_player_name = defaultdict(lambda: defaultdict(str))
# all_player_list includes first and last names for players, player numbers, and teams
all_player_lines = [line.rstrip() for line in open("fantasy_player_data/all_players/all_player_list", 'r')]

for line in all_player_lines[1:]:
	num, name, team = line.rstrip().split(",")

	# get rid of trailing whitespace
	name = re.sub("\s*$", "", name)
	if " " in name:
		last_name = (re.match(".* (.*)$", name)).group(1)
	else: last_name = name

	team_to_player_num[team][last_name] = num
	team_to_player_name[team][num] = name

# team name as String -> Team object
allTeams = {}

# store basic player data
# add players to their corresponding Teams
for line in lines:
	last_name, team, position, price = line.rstrip().split(", ")

	team_dict = check_for_accented_key(team, team_to_player_num);

	num = team_dict[last_name]
	p = classes.Player(last_name, num, team, position, price)

	# store player_name-player_num-player_team = Player object
	key = last_name + "-" + num + "-" + team
	allPlayers[key] = p

	if team not in allTeams:
		allTeams[team] = classes.Team(team, [])

	allTeams[team].addPlayer(p)

# all_player_features[player_num + "-" + team] = {ft_num:ft:value}
all_player_features = defaultdict(lambda: defaultdict(float))

# stores feature number -> feature acronym
feature_num_to_acro = {}
team_to_num_games = defaultdict(float)
for matchday in os.listdir("player_statistics/2015-16/"):
	if matchday.endswith(".py")==False and matchday.endswith("Store")==False:

		folder = "player_statistics/2015-16/" + matchday + "/csv/"
		for tf in os.listdir(folder):
			if tf.endswith("features"):
				if not feature_num_to_acro.keys(): # do this once
					ls = [line.rstrip('\n') for line in open(folder+tf)]
					# store feature number -> feature acronym
					for ft in ls:
						ft_num, ft_acronym = ft.split("\t")
						feature_num_to_acro[ft_num] = ft_acronym
			elif tf.endswith("csv")==False and tf.endswith(".py")==False and tf.endswith(".swp")==False:
				# how to aggregate player stats over multiple matches
				#      - add up stats and then normalize at the end

				# store player features for each Player object as a dict

				# each line is a player
				# for each player in a team, aggregate stats
				# use key: player_num-team
				# for each team, keep a sum of how many games played


				# get team name
				m = re.match("^.*-(.*)$", tf)
				if m:
					team = m.group(1)
					team = re.sub("_", " ", team)
					
					with open((folder+tf), 'r') as team_ft_file:
						for player_line in team_ft_file:
							player_ft = defaultdict(float)
							features = player_line.rstrip().split(",")
							player_num = features[0]
							features = features[1:] # slice off player_num
							if len(features) > 1:
								for ft in features:
									ft_num, ft_val = ft.split(":")
									ft_val = float(ft_val)
									player_ft[ft_num] = ft_val
								def aggregate_player_features(key, team, ft_dict):
									for ft in ft_dict:
										all_player_features[key][ft] += ft_dict[ft]
								key = player_num + "-" + team
								aggregate_player_features(key, team, player_ft)
				team_to_num_games[team] += 1

# normalize player features over num games played
for key in all_player_features:
	team = re.sub(".*-", "", key)
	for player in all_player_features[key]:
		all_player_features[key][player] /= team_to_num_games[team]
	print "%s: " % key, all_player_features[key]

				

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
