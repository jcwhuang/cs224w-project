import collections, util, math, random
import classes, scoring
import copy
import os
import glob
import re
import snap

###---------------------------GLOBALS-------------------------------###
matches = {} #dict of all matches, keys = matchID


def storePDEdges():
  #store 2014-15 and 2015-16 PD EDGE FILES
  # locations = ["passing_distributions/2015-16/", "passing_distributions/2014-15/"]
	locations = ["passing_distributions/2014-15/"]
	for location in locations:
		for matchday in os.listdir(location):
		    if matchday.endswith("sh") or matchday.endswith("py") or matchday.endswith("md") or matchday.endswith("Store"):
		        continue
		    folder = location+matchday+"/networks/"
		    for edge_file in os.listdir(folder):
		        if edge_file.endswith("edges"):
		            matchID = re.search('(.+?)_tpd', edge_file).group(1)
		            team = re.sub("_", " ", re.search('tpd-(.+?)-edges', edge_file).group(1))
		            #these two team names were showing up differently in objects
		            if "Zenit" in team:
		                team = "FC Zenit"
		            elif "Maccabi" in team:
		                team = "Maccabi Tel-Aviv FC"
		            match = classes.Match(team)
		            
		            # right now, setting first team seen with matchID as home team
		            # and second team seen with same matchID is visiting team
		            # TODO: match with games to say who is home team and who is visiting
		            teamObj = classes.Team(team, [])
		            if matchID in matches.keys():
		                match = matches[matchID]
		                match.setVisitingTeam(team)
		                match.setVisitingTeamObj(teamObj)
		                matches[matchID] = match
		                print "matches[%s] = %s" % (matchID, match)
		            else:
		            	match.setHomeTeamObj(teamObj)
		                matches[matchID] = match
		            pd = match.getPD(team)
		            for line in [x.rstrip('\n') for x in open(folder+edge_file)]:
		                elems = line.split('\t')
		                if elems[0] not in pd.keys():
		                    pd[elems[0]] = {}
		                pd[elems[0]][elems[1]] = elems[2]

#TODO
def measureCentrality():
	for matchID in matches.keys():
		print "matchID: %s" % matchID
		match = matches[matchID]
		homePD = match.getPD(match.homeTeam)
		visitingPD = match.getPD(match.visitingTeam)
		# DO SOMETHING
		# compute betweenness centrality for all players and rank top 5

		# load graph
		homeGraph = snap.TUNGraph.New()

		for player1 in homePD:
			for player2 in homePD[player1]:
				player2 = int(player2)
				player1 = int(player1)
				if not homeGraph.IsNode(player1):
					homeGraph.AddNode(player1)
				if not homeGraph.IsNode(player2):
					homeGraph.AddNode(player2)
				homeGraph.AddEdge(player1, player2)

		# calculate betweenness centrality
		Nodes = snap.TIntFltH()
		Edges = snap.TIntPrFltH()
		snap.GetBetweennessCentr(homeGraph, Nodes, Edges, 1.0)
		players_by_between = [(node, Nodes[node]) for node in Nodes]
		players_by_between = sorted(players_by_between, key=lambda(k, v): v, reverse = True)
		print "Top 5 players for %s by betweenness centrality" % (match.homeTeam)
		for i in xrange(5):
			player_name, between = players_by_between[i]
			print player_name, between
		print "--------------"

		# TODO: find corresponding spot in coordinates


def storePlayerCoordinates():
	locations = ["lineup/2014-15/"]  #, "lineup/2015-16/"] #add when 2015-16 lineups done
	for location in locations:
		for matchday in os.listdir(location):
			if "matchday" not in matchday:
				continue
			coordinateLocation = location+matchday+"/coord/"
			for coordFile in os.listdir(coordinateLocation):
				if "csv" not in coordFile or "swp" in coordFile:
					continue
				matchID = re.search('(.+?)_lu', coordFile).group(1)

				teamName = re.sub("_", " ", re.search('lu-(.+?).csv', coordFile).group(1))
				# JADE
				print "teamName is %s" % teamName
				print "match ID is %s" % matchID
				match = matches[matchID]
				print "match is, ", match
				team = match.homeTeamObj
				# JADE
				print "team object is", team
				if team.name != "":
					team = match.visitingTeamObj
				team.name = teamName
				lines = [line.rstrip('\n') for line in open(coordinateLocation+coordFile)]
				goalie = re.sub("# goalie:", "", lines[0])
				goalie = re.sub(" ", "", goalie)

				xcoords = {}
				side = "RIGHT"
				for line in lines[1:]:
					elems = line.split(", ")
					playerNum = elems[0]
					x = elems[1]
					xcoords[playerNum] = x
					if playerNum == goalie:
						if x < 0:
							side = "LEFT"
				if side == "RIGHT":
					for num in xcoords.keys():
						x = int(xcoords[num])
						pos = "DEF"
						if num == goalie:
							pos = "GKP"
						elif x < -90:
							pos = "STR"
						elif x < 70:
							pos = "MID"
						player = classes.Player("", num, teamName, pos, 0)
						team.addPlayer(player)	
				else:
					for num in xcoords.keys():
						x = int(xcoords[num])
						pos = "DEF"
						if num == goalie:
							pos = "GKP"
						elif x > 90:
							pos = "STR"
						elif x > -70:
							pos = "MID"
						player = classes.Player("", num, teamName, pos, 0)
						team.addPlayer(player)			

#returns the position of player with playerNum
def getPosition(team, playerNum):
	for p in team.players:
		if p.number == playerNum:
			return p.position

def classifyPD():
	for matchID in matches.keys():
		# TODO: remove
		if "2014" not in matchID:
			continue

		print "########################"
		print matchID

		match = matches[matchID]
		homeName = match.homeTeam
		visitorName = match.visitingTeam
		home = match.homeTeamObj
		visitor = match.visitingTeamObj
		homePD = match.getPD(homeName)
		visitorPD = match.getPD(visitorName)

		print homeName, " vs ", visitorName

		homeRegionPD = {"DEF": 0, "STR": 0, "MID":0}
		visitorRegionPD = {"DEF": 0, "STR": 0, "MID":0}

		#tally home passes
		for passerNum in homePD.keys():
			for receiverNum in homePD[passerNum].keys():
				receiverPos = getPosition(home, receiverNum)
				if receiverPos == "GKP":
					receiverPos = "DEF"
				if receiverPos != None: #skips players not in starting lineup
					homeRegionPD[receiverPos] += int(homePD[passerNum][receiverNum])

		#tally visitor passes
		for passerNum in visitorPD.keys():
			for receiverNum in visitorPD[passerNum].keys():
				receiverPos = getPosition(visitor, receiverNum)
				if receiverPos == "GKP":
					receiverPos = "DEF"
				if receiverPos != None: #skips players not in starting lineup
					visitorRegionPD[receiverPos] += int(visitorPD[passerNum][receiverNum])

		#classify home PD
		totalPasses = 0
		print homeRegionPD
		for key in homeRegionPD.keys():
			totalPasses += homeRegionPD[key];

		#need to fix this bug, totalPasses = 0 because no player numbers stored
		if totalPasses == 0:
			continue

		defPercentage = float(homeRegionPD["DEF"])/totalPasses
		midPercentage = float(homeRegionPD["MID"])/totalPasses
		strPercentage = float(homeRegionPD["STR"])/totalPasses

		print "DEF: ", str(defPercentage)
		print "MID: ", str(midPercentage)
		print "STR: ", str(strPercentage)

		if defPercentage > 0.5 and midPercentage < 0.4 and strPercentage < 0.4:
			print homeName, "PD: HEAVY DEFENSE"
		elif midPercentage > 0.5 and defPercentage < 0.4 and strPercentage < 0.4:
			print homeName, "PD: HEAVY MIDFIELD"
		elif strPercentage > 0.5 and defPercentage < 0.4 and midPercentage < 0.4:
			print homeName, "PD: HEAVY OFFENSE"
		elif defPercentage < 0.20:
			print homeName, "PD: LIGHT DEFENSE"
		elif midPercentage < 0.20:
			print homeName, "PD: LIGHT MIDFIELD"
		elif strPercentage < 0.20:
			print homeName, "PD: LIGHT OFFENSE"
		else:
			print homeName, "PD: BALANCED"

		#classify visitor PD
		totalPasses = 0
		print visitorRegionPD
		for key in visitorRegionPD.keys():
			totalPasses += visitorRegionPD[key];

		#need to fix this bug, totalPasses = 0 because no player numers stored
		if totalPasses == 0:
			continue

		defPercentage = float(visitorRegionPD["DEF"])/totalPasses
		midPercentage = float(visitorRegionPD["MID"])/totalPasses
		strPercentage = float(visitorRegionPD["STR"])/totalPasses

		print "DEF: ", str(defPercentage)
		print "MID: ", str(midPercentage)
		print "STR: ", str(strPercentage)

		if defPercentage > 0.5 and midPercentage < 0.4 and strPercentage < 0.4:
			print visitorName, "PD: HEAVY DEFENSE"
		elif midPercentage > 0.5 and defPercentage < 0.4 and strPercentage < 0.4:
			print visitorName, "PD: HEAVY MIDFIELD"
		elif strPercentage > 0.5 and defPercentage < 0.4 and midPercentage < 0.4:
			print visitorName, "PD: HEAVY OFFENSE"
		elif defPercentage < 0.20:
			print visitorName, "PD: LIGHT DEFENSE"
		elif midPercentage < 0.20:
			print visitorName, "PD: LIGHT MIDFIELD"
		elif strPercentage < 0.20:
			print visitorName, "PD: LIGHT OFFENSE"
		else:
			print visitorName, "PD: BALANCED"







###-----------------------Run Script---------------------------###

#Rank each player by centrality measures
storePDEdges()

measureCentrality()  #TODO

#Find each player's location using tactical lineup coordinates
storePlayerCoordinates()

#Tally up total passes in each field region
classifyPD()

#Determine passing distribution classification


#to check
'''for key in matches.keys():
	print key
	home = matches[key].homeTeam
	print home
	for player in matches[key].homeTeamObj.players:
		print player.number
		print player.position
	visitor =  matches[key].visitingTeam
	print visitor
	for player in matches[key].visitingTeamObj.players:
		print player.number
		print player.position
	print "########################################"
'''
