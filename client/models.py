#-*- coding:utf8 -*-

from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta

class SingleRanking(models.Model):
    player = models.ForeignKey(User, related_name='player', unique=True)
    points = models.FloatField(default=None, null=True)
    rank = models.IntegerField(default=None, null=True)
    game_count = models.IntegerField(default=None, null=True)

    @staticmethod
    def findOrCreate(pl):
        try:
            return SingleRanking.objects.get(player=pl)
        except SingleRanking.DoesNotExist:
            new = SingleRanking(player=pl)
            return new

class AverageMatchStat(models.Model):
    player_a = models.ForeignKey(User, related_name='player_a')
    player_b = models.ForeignKey(User, related_name='player_b')
    score_a = models.FloatField(null=True)
    score_b = models.FloatField(null=True)
    game_count = models.IntegerField(null=True)

    @staticmethod
    def findOrCreate(pl_a, pl_b):
        try:
            return AverageMatchStat.objects.get(player_a=pl_a, player_b=pl_b)
        except AverageMatchStat.DoesNotExist:
            new = AverageMatchStat(player_a=pl_a, player_b=pl_b)
            return new

    @staticmethod
    def getForUser(user):
        return AverageMatchStat.objects.extra(where=['(player_a_id = %s or player_b_id = %s) and score_a IS NOT NULL'], params=[user.id, user.id])

class DoubleRanking(models.Model):
    first_player = models.ForeignKey(User, related_name='first_player')
    second_player = models.ForeignKey(User, related_name='second_player')
    points = models.FloatField(default=None, null=True)

    class Meta:
        unique_together = (('first_player', 'second_player'),)

    def __unicode__(self):
        names = []
        names.append(self.first_player.first_name)
        names.append(self.second_player.first_name)
        names.sort()
        return u' – '.join(names)

    @staticmethod
    def findOrCreate(pl_a, pl_b):
        if pl_a.id > pl_b.id:
            (pl_a, pl_b) = (pl_b, pl_a)

        try:
            return DoubleRanking.objects.get(first_player=pl_a, second_player=pl_b)
        except DoubleRanking.DoesNotExist:
            new = DoubleRanking(first_player = pl_a, second_player = pl_b)
            return new

class Game(models.Model):
    team_a_1 = models.ForeignKey(User, related_name='team_a_1')
    team_a_2 = models.ForeignKey(User, related_name='team_a_2', null=True)
    team_b_1 = models.ForeignKey(User, related_name='team_b_1')
    team_b_2 = models.ForeignKey(User, related_name='team_b_2', null=True)
    game_time = models.DateTimeField(auto_now_add=True)
    score_a = models.IntegerField()
    score_b = models.IntegerField()
    score_base = models.IntegerField(choices=(('11', '11'), ('21', '21'))) # 11 or 21
    referee = models.ForeignKey(User, related_name='referee')

    def __unicode__(self):
        return "%s vs. %s" % (
            self.team_a_1.first_name if self.team_a_2 == None else "%s & %s" % (self.team_a_1.first_name, self.team_a_2.first_name),
            self.team_b_1.first_name if self.team_b_2 == None else "%s & %s" % (self.team_b_1.first_name, self.team_b_2.first_name),
            )

    def isDouble(self):
        return self.team_a_2 and self.team_b_2

def computePoints():
    # Select all the games for the last month
    all_games = Game.objects.filter(game_time__gte=datetime.now()-timedelta(days=30))

    single_acc = {}
    double_acc = {}
    player_count = {}
    avg_score = {}

    def __setAccPoints(acc, a, b, p):
        if (a.id > b.id):
            (a, b) = (b, a)
            p = -p
        k = '%0u-%0u' % (a.id, b.id)
        i = acc.setdefault(k, {'a':a, 'b':b, 's': 0.0, 'c': 0})
        i['s'] += p
        i['c'] += 1

    for game in all_games:
        points = (game.score_a-game.score_b)
        points -= cmp(points, 0)*2 #Substract the default difference from the bonus
        points *= 21.0/game.score_base #normalize as if a 21pts game
        points += cmp(points, 0) * 10 #bonus for winning
        if game.isDouble():
            __setAccPoints(
                double_acc,
                DoubleRanking.findOrCreate(game.team_a_1, game.team_a_2),
                DoubleRanking.findOrCreate(game.team_b_1, game.team_b_2),
                points
            )
        else:
            player_count[game.team_a_1] = player_count.setdefault(game.team_a_1, 0) + 1
            player_count[game.team_b_1] = player_count.setdefault(game.team_b_1, 0) + 1
            (pta, ptb) = (game.score_a, game.score_b)
            if game.score_base == 11:
                pta *= 21.0/11.0
                ptb *= 21.0/11.0
            if (game.team_a_1.id < game.team_b_1.id):
                avg_key = '%0u-%0u' % (game.team_a_1.id, game.team_b_1.id)
                avg = avg_score.setdefault(avg_key, {'a': game.team_a_1, 'b': game.team_b_1, 'sa': 0, 'sb': 0, 'c': 0})
                avg['sa'] += pta
                avg['sb'] += ptb
                avg['c']  += 1
            else:
                avg_key = '%0u-%0u' % (game.team_b_1.id, game.team_a_1.id)
                avg = avg_score.setdefault(avg_key, {'a': game.team_b_1, 'b': game.team_a_1, 'sa': 0, 'sb': 0, 'c': 0})
                avg['sa'] += ptb
                avg['sb'] += pta
                avg['c']  += 1
            __setAccPoints(
                single_acc,
                SingleRanking.findOrCreate(game.team_a_1),
                SingleRanking.findOrCreate(game.team_b_1),
                points
            )

    AverageMatchStat.objects.all().update(score_a=None, score_b=None, game_count=None)

    for avg in avg_score.values():
        score = AverageMatchStat.findOrCreate(avg['a'], avg['b'])
        score.score_a = avg['sa'] / avg['c']
        score.score_b = avg['sb'] / avg['c']
        score.game_count = avg['c']
        score.save()

    pp = {}

    for v in single_acc.itervalues():
        a = pp.setdefault(v['a'], {'s': 0.0, 'c': 0})
        b = pp.setdefault(v['b'], {'s': 0.0, 'c': 0})
        a['s'] += v['s']
        a['c'] += v['c']
        b['s'] -= v['s']
        b['c'] += v['c']

    #reset all scores
    SingleRanking.objects.all().update(points=None, game_count=None, rank=None)

    for (rank, points) in pp.items():
        rank.points = points['s'] / points['c']
        rank.game_count = player_count[rank.player]
        rank.save()

    position = 1
    for rank in SingleRanking.objects.filter(game_count__isnull=False).order_by('-points'):
        rank.rank = position
        rank.save()
        position += 1

    pp = {}

    for v in double_acc.itervalues():
        a = pp.setdefault(v['a'], {'s': 0.0, 'c': 0})
        b = pp.setdefault(v['b'], {'s': 0.0, 'c': 0})
        a['s'] += v['s']
        a['c'] += v['c']
        b['s'] -= v['s']
        b['c'] += v['c']

    #reset all scores
    DoubleRanking.objects.all().update(points=None)

    for (rank, points) in pp.items():
        rank.points = points['s'] / points['c']
        rank.save()



class InvalidScore(Exception):
    pass
