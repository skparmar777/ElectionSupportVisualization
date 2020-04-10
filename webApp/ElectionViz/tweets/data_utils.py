import copy

class TweetsData:
    def __init__(self, username, tweet_text, likes, sentiment, tweet_date, date_descriptor):
        self.username = username
        self.tweet_text = tweet_text
        self.likes = likes
        self.sentiment = round(sentiment, 2)
        self.tweet_date = tweet_date
        self.date_descriptor = date_descriptor

    def __ge__(self, tweets_data):
        return self.likes >= tweets_data.likes

    def asdict(self):
        ret = {}
        ret['username'] = self.username
        ret['tweet_text'] = self.tweet_text.replace('\n', ' ').replace('\\', '').replace('"', "'")
        ret['likes'] = self.likes
        ret['sentiment'] = self.sentiment
        ret['tweet_date'] = self.tweet_date.strftime('%B %d at %H:%M')
        ret['date_descriptor'] = self.date_descriptor
        return ret

class CandidatePolarity:
    def __init__(self, polarity, total_likes, num_tweets, avg_sentiment, tweet):
        self.polarity = polarity
        self.total_likes = total_likes
        self.num_tweets = num_tweets
        self.avg_sentiment = avg_sentiment
        self.tweet = tweet

    def combine(self, candidate_polarity):
        if candidate_polarity is None:
            return copy.deepcopy(self)
        polarity = self.polarity if self.polarity == candidate_polarity.polarity else None
        total_likes = self.total_likes + candidate_polarity.total_likes
        num_tweets = self.num_tweets + candidate_polarity.num_tweets
        avg_sentiment = (self.avg_sentiment * self.num_tweets + candidate_polarity.avg_sentiment * candidate_polarity.num_tweets) / num_tweets
        tweet = self.tweet if self.tweet >= candidate_polarity.tweet else candidate_polarity.tweet
        return CandidatePolarity(polarity, total_likes, num_tweets, avg_sentiment, tweet)

    def asdict(self):
        ret = {}
        ret['polarity'] = self.polarity
        ret['total_likes'] = self.total_likes
        ret['num_tweets'] = self.num_tweets
        ret['avg_sentiment'] = self.avg_sentiment
        ret['tweet'] = self.tweet.asdict()
        return ret

class Candidate:
    def __init__(self, candidate):
        self.candidate = candidate
        self.pos = None
        self.neg = None
        self.combined = None

    def insert_polarity(self, candidate_polarity):
        if candidate_polarity.polarity == 'P':
            if self.pos is None:
                self.pos = candidate_polarity
            else:
                self.pos = self.pos.combine(candidate_polarity)
        else:
            if self.neg is None:
                self.neg = candidate_polarity
            else:
                self.neg = self.neg.combine(candidate_polarity)

    def add_pos(self, pos):
        self.pos = pos

    def add_neg(self, neg):
        self.neg = neg
        
    def combine_pos_neg(self):
        self.combined = self.pos.combine(self.neg) if self.pos is not None else copy.deepcopy(self.neg)

    def combine(self, candidate):
        c = self.candidate if self.candidate == candidate.candidate else None
        new_candidate = Candidate(c)
        pos = self.pos.combine(candidate.pos) if self.pos is not None else copy.deepcopy(candidate.pos)
        neg = self.neg.combine(candidate.neg) if self.neg is not None else copy.deepcopy(candidate.neg)
        new_candidate.add_pos(pos)
        new_candidate.add_neg(neg)
        return new_candidate

    def asdict(self):
        ret = {}
        ret['P'] = self.pos.asdict() if self.pos is not None else 'null'
        ret['N'] = self.neg.asdict() if self.neg is not None else 'null'
        ret['combined'] = self.combined.asdict() if self.combined is not None else 'null'
        return ret

class Party:
    def __init__(self, party):
        self.party = party
        self.candidates = []
        self.candidate_to_idx = dict()
        self.combined = None

    def add_candidate(self, candidate):
        self.candidates.append(candidate)
        self.candidate_to_idx[candidate.candidate] = len(self.candidates) - 1

    def combine_candidates(self):
        if len(self.candidates) == 0:
            return
        self.combined = self.candidates[0]
        for i in range(1, len(self.candidates)):
            self.combined = self.combined.combine(self.candidates[i])
        self.combined.combine_pos_neg()

    def asdict(self):
        if len(self.candidates) == 0:
            return 'null'
        ret = {}
        for c in self.candidates:
            ret[c.candidate] = c.asdict()
        ret['combined'] = self.combined.asdict() if self.combined is not None else 'null'
        return ret

    def combine(self, party):
        if len(party.candidates) == 0:
            return copy.deepcopy(self)
        new_party = Party(self.party)
        done = set()
        for c, i in self.candidate_to_idx.items():
            new_c = self.candidates[i]
            if c in party.candidate_to_idx:
                new_c = new_c.combine(party.candidates[party.candidate_to_idx[c]])
                new_c.combine_pos_neg()
            new_party.add_candidate(new_c)
            done.add(c)
        for c, i in party.candidate_to_idx.items():
            if c in done:
                continue
            # remaining candidates only in other party
            new_c = party.candidates[i]
            new_party.add_candidate(new_c)

        new_party.combine_candidates()
        return new_party

