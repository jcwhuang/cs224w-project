import collections

# stores relevant team data
class Team():
	def __init__(self, name, players):
		self.name = name
		self.players = players
		self.rank = 0

	def setRank(self, rank):
		self.rank = rank

	def addPlayer(self, player):
		self.players.append(player)

class Player():
	def __init__(self, name, team, position, price):
		#self.firstName = firstName
		#self.lastName = lastName
		self.name = name
		self.team = team
		self.position = position
		self.price = price
		self.matches = []
		self.stats = []

class MatchPlayerStats():
	def __init__(self):
		self.minutes = 0
		self.goals = 0
		self.attemptsHittingBar = 0
		self.foulsSuffered = 0
		self.attemptsOffTarget = 0
		self.offsides = 0
		self.attemptsOnTarget = 0
		self.attemptsBlocked = 0
		self.yellowCards = 0
		self.attemptsHittingPost = 0
		self.foulsCommitted = 0
		self.redCards = 0

class Match():
	def __init__(self, homeTeam, visitingTeam):
		self.homeTeam = homeTeam
		self.visitingTeam = visitingTeam
		self.homeScore = 0
		self.visitorScore = 0

	def winner(self):
		if self.homeScore > self.visitorScore:
			return self.homeTeam
		elif self.homeScore < self.visitorScore:
			return self.visitingTeam
		else:
			return "DRAW"

	def setHomeScore(self, score):
		self.homeScore = score

	def setVisitorScore(self, score):
		self.visitorScore = score

