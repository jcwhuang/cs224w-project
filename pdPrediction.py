import collections, util, math, random
import classes, scoring
import copy
import os
import glob
import re
from collections import defaultdict
import unicodedata


#----------------------Store all player and team data-------------------#
# list of all players as Players
allPlayers = {}

# for positions, only last names are included along with price, team, and position
lines = [line.rstrip('\n') for line in open('fantasy_player_data/positions/defenders')]
lines += [line.rstrip('\n') for line in open('fantasy_player_data/positions/forwards')]
lines += [line.rstrip('\n') for line in open('fantasy_player_data/positions/goalkeepers')]
lines += [line.rstrip('\n') for line in open('fantasy_player_data/positions/midfielders')]

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
	price = float(price)
	team_dict = check_for_accented_key(team, team_to_player_num);

	num = team_dict[last_name]
	p = classes.Player(last_name, num, team, position, price)

	# store player_name-player_num-player_team = Player object
	key = last_name + "-" + num + "-" + team
	allPlayers[key] = p

	if team not in allTeams:
		allTeams[team] = classes.Team(team, [])

	allTeams[team].addPlayer(p)

print allTeams.keys()

#------------------END storing of all player and team data-------------------#

def findPlayerPosition(name, team):
	teamObj = allTeams[team]
	splitName = name.split(" ")
	lastName = splitName[len(splitName)-1]

	for player in teamObj.players:
		if player.name == lastName:
			return player.position

	return "MID"  #returns "MID" when player not found in team
				#occurs only for a few players

#store team rankings, teamName:ranking
rankings = {}
for line in [x.rstrip('\n') for x in open("rankings.txt")]:
	sl = line.split('\t')
	rankings[sl[0]] = sl[1]

#matchID:classes.Match
matches = {}

#store matches with teams and players (just nodes files)
for matchday in os.listdir("passing_distributions/2015-16/"):
	if matchday.endswith("sh") or matchday.endswith("py") or matchday.endswith("md") or matchday.endswith("Store"):
		continue
	folder = "passing_distributions/2015-16/"+matchday+"/networks/"
	for nodes_file in os.listdir(folder):
		if nodes_file.endswith("nodes"):
			matchID = re.search('(.+?)_tpd', nodes_file).group(1)
			team = re.sub("_", " ", re.search('tpd-(.+?)-nodes', nodes_file).group(1))

			#these two team names were showing up differently in objects
			if "Zenit" in team:
				team = "FC Zenit"
			elif "Maccabi" in team:
				team = "Maccabi Tel-Aviv FC"

			teamObj = classes.Team(team, [])
			for line in [x.rstrip('\n') for x in open(folder+nodes_file)]:
				elems = line.split('\t')
				playerName = re.sub("\s*$", "", elems[1])
				position = findPlayerPosition(playerName, team)
				player = classes.Player(playerName, elems[0], team, position, 0)
				teamObj.addPlayer(player)

			if matchID not in matches.keys():
				match = classes.Match(team, "")
				match.setHomeTeamObj(teamObj)
				matches[matchID] = match
			else:
				match = matches[matchID]
				match.setVisitingTeam(team)
				match.setVisitingTeamObj(teamObj)


#store passing distributions for each match
for matchday in os.listdir("passing_distributions/2015-16/"):
	if matchday.endswith("sh") or matchday.endswith("py") or matchday.endswith("md") or matchday.endswith("Store"):
		continue
	folder = "passing_distributions/2015-16/"+matchday+"/networks/"
	for edge_file in os.listdir(folder):
		if edge_file.endswith("edges"):
			matchID = re.search('(.+?)_tpd', edge_file).group(1)
			team = re.sub("_", " ", re.search('tpd-(.+?)-edges', edge_file).group(1))

			#these two team names were showing up differently in objects
			if "Zenit" in team:
				team = "FC Zenit"
			elif "Maccabi" in team:
				team = "Maccabi Tel-Aviv FC"

			match = matches[matchID]
			pd = match.getPD(team)

			for line in [x.rstrip('\n') for x in open(folder+edge_file)]:
				elems = line.split('\t')
				
				if elems[0] not in pd.keys():
					pd[elems[0]] = {}
				pd[elems[0]][elems[1]] = elems[2]


#store team ranks in matches
for matchID in matches.keys():
	match = matches[matchID]
	match.homeTeamObj.setRank(rankings[match.homeTeam])
	match.visitingTeamObj.setRank(rankings[match.visitingTeam])


def computePositionPD(team, pd, players):
	num_to_pos = {}
	for player in players:
		num_to_pos[player.number] = player.position
	passes_to_pos = collections.Counter()
	for player in pd.keys():
		for receiver in pd[player].keys():
			pos = num_to_pos[receiver]
			passes_to_pos[pos] += int(pd[player][receiver])

	return passes_to_pos

# compute PD types for each team in each match
for id in matches.keys():
	match = matches[id]
	match.homePosPD = computePositionPD(match.homeTeam, match.homePD, match.homeTeamObj.players)
	match.visitorPosPD = computePositionPD(match.visitingTeam, match.visitorPD, match.visitingTeamObj.players)

	#to do some more analysis
	print "#################################################"
	print "MATCH ", id
	print match.homeTeam, " (#", rankings[match.homeTeam],") vs ", match.visitingTeam, " (#", rankings[match.visitingTeam], ")"
	print match.homeTeam, "'s position PD: "
	print match.homePosPD
	print match.visitingTeam, "'s position PD: "
	print match.visitorPosPD
	print "#################################################"

#TO CHECK
'''for id in matches.keys():
	print id
	print matches[id].homeTeam
	print matches[id].getPD(matches[id].homeTeam)
	print matches[id].visitingTeam
	print matches[id].getPD(matches[id].visitingTeam)
'''	
#	print matches[id].homeTeamObj.players[0].name
#	print matches[id].visitingTeam
#	print matches[id].visitingTeamObj.players[0].name
	

'''m = re.search('AAA(.+?)ZZZ', text)
if m:
    found = m.group(1)
'''
