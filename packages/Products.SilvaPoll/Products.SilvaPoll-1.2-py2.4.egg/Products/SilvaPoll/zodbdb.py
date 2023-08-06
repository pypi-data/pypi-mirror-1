from Persistence import Persistent

class Question:
    def __init__(self, question, answers):
        self.question = question
        self.answers = answers
        self.votes = len(answers) * [0]

    def vote(self, index):
        self.votes[index] += 1

class DB(Persistent):
    def __init__(self, context):
        # we don't need the context here, it's only useful in situations
        # where we want to actually get stuff from the ZODB (like SQL
        # connections)
        self.db = []

    def create(self, question, answers, votes):
        assert len(votes) == len(answers), 'votes and answers don\'t match!'
        q = (question, answers, votes)
        self.db.append(q)
        self._p_changed = True
        # note that removing els from the db breaks things big-time
        return len(self.db) - 1

    def get(self, id):
        data = self.db[id]
        q = Question(*data[:2])
        q.votes = data[2]
        return q

    def update(self, id, question, answers):
        votes = len(answers) * [0]
        try:
            current = self.get(id)
        except IndexError:
            pass
        else:
            # note that if the number of answers doesn't match, we blatantly 
            # throw away any existing votes (since we can't really know 
            # what votes to keep)
            if len(current.votes) == len(answers):
                votes = current.votes
        self.db[id] = (question, answers, votes)
        self._p_changed = True

    def vote(self, id, index):
        q = self.db[id]
        q[2][index] += 1
        self.db[id] = q
        self._p_changed = True
