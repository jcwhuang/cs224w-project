import collections

# stores relevant team data
class Team():
	def __init__(self, name):
		self.name = name
		self.players = []
		self.rank = 0

	def setRank(self, rank):
		self.rank = rank

class Player():
	def __init__(self, firstName, lastName, position):
		self.firstName = firstName
		self.lastName = lastName
		self.position = position

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

