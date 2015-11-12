import collections, random, math

# An abstract class representing a Markov Decision Process (MDP).
class MDP:
    # Return the start state.
    def startState(self): raise NotImplementedError("Override me")

    # Return set of actions possible from |state|.
    def actions(self, state): raise NotImplementedError("Override me")

    # Return a list of (newState, prob, reward) tuples corresponding to edges
    # coming out of |state|.
    # Mapping to notation from class:
    #   state = s, action = a, newState = s', prob = T(s, a, s'), reward = Reward(s, a, s')
    # If IsEnd(state), return the empty list.
    def succAndProbReward(self, state, action): raise NotImplementedError("Override me")

    def discount(self): raise NotImplementedError("Override me")

    # Compute set of states reachable from startState.  Helper function for
    # MDPAlgorithms to know which states to compute values and policies for.
    # This function sets |self.states| to be the set of all states.
    def computeStates(self):
        self.states = set()
        queue = []
        self.states.add(self.startState())
        queue.append(self.startState())
        while len(queue) > 0:
            state = queue.pop()
            for action in self.actions(state):
                for newState, prob, reward in self.succAndProbReward(state, action):
                    if newState not in self.states:
                        self.states.add(newState)
                        queue.append(newState)
        # print "%d states" % len(self.states)
        # print self.states


############################################################

# An algorithm that solves an MDP (i.e., computes the optimal
# policy).
class MDPAlgorithm:
    # Set:
    # - self.pi: optimal policy (mapping from state to action)
    # - self.V: values (mapping from state to best values)
    def solve(self, mdp): raise NotImplementedError("Override me")

############################################################

# Abstract class: an RLAlgorithm performs reinforcement learning.  All it needs
# to know is the set of available actions to take.  The simulator (see
# simulate()) will call getAction() to get an action, perform the action, and
# then provide feedback (via incorporateFeedback()) to the RL algorithm, so it can adjust
# its parameters.
class RLAlgorithm:
    # Your algorithm will be asked to produce an action given a state.
    def getAction(self, state): raise NotImplementedError("Override me")

    # We will call this function when simulating an MDP, and you should update
    # parameters.
    # If |state| is a terminal state, this function will be called with (s, a,
    # 0, None). When this function is called, it indicates that taking action
    # |action| in state |state| resulted in reward |reward| and a transition to state
    # |newState|.
    def incorporateFeedback(self, state, action, reward, newState): raise NotImplementedError("Override me")

# An RL algorithm that acts according to a fixed policy |pi| and doesn't
# actually do any learning.
class FixedRLAlgorithm(RLAlgorithm):
    def __init__(self, pi): self.pi = pi

    # Just return the action given by the policy.
    def getAction(self, state): return self.pi[state]

    # Don't do anything: just stare off into space.
    def incorporateFeedback(self, state, action, reward, newState): pass

############################################################

# Perform |numTrials| of the following:
# On each trial, take the MDP |mdp| and an RLAlgorithm |rl| and simulates the
# RL algorithm according to the dynamics of the MDP.
# Each trial will run for at most |maxIterations|.
# Return the list of rewards that we get for each trial.
def simulate(mdp, rl, numTrials=10, maxIterations=1000, verbose=False,
             sort=False):
    # Return i in [0, ..., len(probs)-1] with probability probs[i].
    def sample(probs):
        target = random.random()
        accum = 0
        for i, prob in enumerate(probs):
            accum += prob
            if accum >= target: return i
        raise Exception("Invalid probs: %s" % probs)

    totalRewards = []  # The rewards we get on each trial
    for trial in range(numTrials):
        state = mdp.startState()
        sequence = [state]
        totalDiscount = 1
        totalReward = 0
        for _ in range(maxIterations):
            action = rl.getAction(state)
            transitions = mdp.succAndProbReward(state, action)

            # TO CHECK
            print "state = ", str(state)
            print "chosen action = ", str(action)

            if sort: transitions = sorted(transitions)
            if len(transitions) == 0:

                #TO CHECK
                print "len(transitions) = 0"
                print "Transitions: ", str(transitions)

                rl.incorporateFeedback(state, action, 0, None)
                break

            # Choose a random transition
            i = sample([prob for newState, prob, reward in transitions])
            newState, prob, reward = transitions[i]
            sequence.append(action)
            sequence.append(reward)
            sequence.append(newState)

            rl.incorporateFeedback(state, action, reward, newState)
            totalReward += totalDiscount * reward
            totalDiscount *= mdp.discount()
            state = newState
            print "iteration ", _, ", reward = reward"
        if verbose:
            print "Trial %d (totalReward = %s): %s" % (trial, totalReward, sequence)
            print ""
        totalRewards.append(totalReward)
    return totalRewards

# Performs Q-learning.  Read util.RLAlgorithm for more information.
# actions: a function that takes a state and returns a list of actions.
# discount: a number between 0 and 1, which determines the discount factor
# featureExtractor: a function that takes a state and action and returns a list of (feature name, feature value) pairs.
# explorationProb: the epsilon value indicating how frequently the policy
# returns a random action
class QLearningAlgorithm(RLAlgorithm):
    def __init__(self, actions, discount, featureExtractor, explorationProb=0.2):
        self.actions = actions
        self.discount = discount
        self.featureExtractor = featureExtractor
        self.explorationProb = explorationProb
        self.weights = collections.Counter()
        self.numIters = 0


   # Return the Q function associated with the weights and features
    def getQ(self, state, action):
        score = 0
        for f, v in self.featureExtractor(state, action):
            score += self.weights[f] * v
        return score

    # This algorithm will produce an action given a state.
    # Here we use the epsilon-greedy algorithm: with probability
    # |explorationProb|, take a random action.
    def getAction(self, state):
        self.numIters += 1

        if random.random() < self.explorationProb:
            return random.choice(self.actions(state))
        else:

            #TO CHECK
            sub = [self.getQ(state,action) for action in self.actions(state)]
            print "sub = ", str(sub)
            #--------------------------

            maxQ = max((self.getQ(state,action)) for action in self.actions(state))			
            qs = [(self.getQ(state, action), action) for action in self.actions(state) if self.getQ(state,action)==maxQ]
            #return max((self.getQ(state, action), action) for action in self.actions(state))[1]
            return qs[random.randint(0, len(qs)-1)][1]
    # Call this function to get the step size to update the weights.
    def getStepSize(self):
        return 1.0 / math.sqrt(self.numIters)

    # We will call this function with (s, a, r, s'), which you should use to update |weights|.
    # Note that if s is a terminal state, then s' will be None.  Remember to check for this.
    # You should update the weights using self.getStepSize(); use
    # self.getQ() to compute the current estimate of the parameters.
    def incorporateFeedback(self, state, action, reward, newState):
        # BEGIN_YOUR_CODE (around 15 lines of code expected)

        #check for end state
        if newState == None:
            return

        Vopt = max([self.getQ(newState, a) for a in self.actions(newState)])
        Qopt = self.getQ(state, action)
        for name, value in self.featureExtractor(state, action):
            self.weights[name] -= self.getStepSize()*(Qopt - (reward + self.discount*Vopt))*value
        # END_YOUR_CODE

# Return a singleton list containing indicator feature for the (state, action)
# pair.  Provides no generalization.
def identityFeatureExtractor(state, action):
    featureKey = (state, action)
    featureValue = 1
    return [(featureKey, featureValue)]

def fantasyFeatureExtractor(state, action):
    '''playedInGame = False    # 1pt
	played60Min = False     # 2pt
	goalsScored = 0         # 6pt if GK or DEF, 5pt if MID, 4 if STR
	assists = 0             # 3pt
	noScoreOnGK = False     # 4pt if played 60min
	noScoreOnDEF = False    # 4pt if played 60min
	noScoreOnMID = False    # 1pt if played 60min
	penaltiesReceived = 0   # 1pt 
	penaltiesConceded = 0   # -1pt 
	penaltyMisses = 0       # -2pt
	penaltySaves = 0        # 5pt
	goalsConceded = 0       # -1pt/2goals for GK or MID
	yellowCard = False      # -1pt
	redCard = False         # -3pt
	savesByGK = 0           # 1pt/3saves
	recoveredBalls = 0      # 1pt/5balls
    '''
    roster = state[0]
    features = []

    gamesPlayed = 0
    teamMinutes = 0
    teamGoals = 0
    teamAssists = 0
    teamShutOuts = 0
    penaltiesReceived = 0
    penaltiesConceded = 0
    penaltiesMissed = 0
    penaltiesSaved = 0
    goalsConceded = 0
    yellowCards = 0
    savesByGK = 0
    recoveredBalls = 0
    redCards = 0

	#non-fantasy-score features
    foulsCommitted = 0
    foulsSuffered = 0
    attemptsOffTarget = 0
    offsides = 0
    attemptsOnTarget = 0
    attemptsBlocked = 0

    for player in roster: 
        gamesPlayed += 1	
        teamMinutes += player.stats['M']
        teamGoals += player.stats['G']
        yellowCards += player.stats['Y']
        redCards += player.stats['R']

        #non-fantasy-score features
        foulsCommitted += player.stats['FC']
        foulsSuffered += player.stats['FS']
        attemptsOffTarget += player.stats['W']
        offsides += player.stats['O']
        attemptsOnTarget += player.stats['T']
        attemptsBlocked += player.stats['AB']	

        # teamMinutes += matchStats.minutes
        # teamGoals += matchStats.goals
        # yellowCards += matchStats.yellowCards
        # redCards += matchStats.redCards

        # #non-fantasy-score features
        # foulsCommitted += matchStats.foulsCommitted
        # foulsSuffered += matchStats.foulsSuffered 
        # attemptsOffTarget += matchStats.attemptsOffTarget
        # offsides += matchStats.offsides
        # attemptsOnTarget += matchStats.attemptsOnTarget
        # attemptsBlocked += matchStats.attemptsBlocked

		#(NOT IN PLAYER SUMMARY STATS)
        '''teamAssists
        penaltiesReceived 
        penaltiesConceded
        penaltiesMissed
        penaltiesSaved
        teamShutouts
        savesByGK
        recoveredBalls
        goalsConceded
        '''
        #can also add opposing team features
    features.append(('gamesPlayed', gamesPlayed))			
    features.append(('teamMinutes', teamMinutes))
    features.append(('teamGoals', teamGoals))   
    features.append(('yellowCards', yellowCards))
    features.append(('redCards', redCards))
    #non-fantasy-score features
    features.append(('foulsCommitted', foulsCommitted))
    features.append(('foulsSuffered', foulsSuffered))
    features.append(('attemptsOffTarget', attemptsOffTarget))
    features.append(('offsides', offsides))
    features.append(('attemptsOnTarget', attemptsOnTarget))
    features.append(('attemptsBlocked', attemptsBlocked))

    return features
