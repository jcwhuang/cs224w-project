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

	def __str__( self ):
		return self.name + "," + str(self.players) + "," + str(self.rank)

class Player():
	def __init__(self, name, number, team, position, price):
		#self.firstName = firstName
		#self.lastName = lastName
		self.name = name
		self.number = number
		self.team = team
		self.position = position
		self.price = price
		self.matches = []
		self.stats = []

	def __str__( self ):
		return self.name, ",", self.number,",", self.team,",", self.position, \
			",", self.price,",",self.matches,",",self.stats

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
	# def __init__(self, homeTeam, visitingTeam):
	def __init__(self, homeTeam):

		self.homeTeam = homeTeam
		# self.visitingTeam = visitingTeam

		self.visitingTeam = ""
		self.homeScore = 0
		self.visitorScore = 0
		self.homeTeamObj = Team("", "")
		self.visitingTeamObj = Team("", "")
		self.homePD = {}
		self.visitorPD = {}

		#stores how many passes to defenders, mids, etc.
		self.homePosPD = {}
		self.visitorPosPD = {}

		# can be one of "HEAVY_DEF", "HEAVY_MID", "HEAVY_OFF", "BALANCED", 
		# still need to add possibility of "HEAVY_RIGHT" and "HEAVY_LEFT"
		# in pdPrediction.py
		self.homePDType = ""
		self.visitorPDType = ""

	def __str__( self ):
		return "" + self.homeTeam +  "," + self.visitingTeam

	def getPD(self, team):
		if team == self.homeTeam:
			return self.homePD
		return self.visitorPD

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

	def setHomeTeam(self, team):
		self.homeTeam = team

	def setVisitingTeam(self, team):
		self.visitingTeam = team

	def setHomeTeamObj(self, team):
		self.homeTeamObj = team

	def setVisitingTeamObj(self, team):
		self.visitingTeamObj = team




