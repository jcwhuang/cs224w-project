import collections
import re
import classes
import scoring

# for rankings: key = team name, value = ranking

#returns the dict rankings where keys are team names and values are corresponding rankings
def getRankings():
	lines = [line.rstrip('\n') for line in open('rankings.txt')]
	rankings = {}
	for line in lines:
		r = re.sub("[^\w]", " ", line).split()
		rankings[r[1]] = r[0]
	return rankings

def predictMatches(matches, rankings, verbose=False):
	predictions = []
	for m in matches:
		team1, team2 = m.homeTeam, m.visitingTeam
		match = classes.Match(team1, team2)
		ranking1, ranking2 = 100, 100
		if team1 not in rankings.keys():
			if (verbose):
				print "Team 1 not found: " + team1
		else:
			ranking1 = rankings[team1]
		if team2 not in rankings.keys():
			if (verbose):
				print "Team 2 not found: " + team2
		else:
			ranking2 = rankings[team2]
		if ranking1 < ranking2:
			if (verbose):
				print "Winner: " + team1
			match.setHomeScore(1)
			match.setVisitorScore(0)
		elif ranking1 > ranking2:
			if (verbose):
				print "Winner: " + team2
			match.setHomeScore(0)
			match.setVisitorScore(1)
		predictions.append(match)

	return predictions
	
def main():
	rankings = getRankings()
	matches = []
	lines = [line.rstrip('\n') for line in open('matches_groupStage_2014_15_Champions.txt')]
	for line in lines:
		r = re.sub("[^\w]", " ", line).split()
		m = classes.Match(r[0], r[3])
		m.setHomeScore(r[1])
		m.setVisitorScore(r[2])
		matches.append(m)

	predictions = predictMatches(matches, rankings, verbose=False)
	scoring.score(matches, predictions)

if __name__ == '__main__':
	main()


