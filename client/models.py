#-*- coding:utf8 -*-

from django.db import models
from datetime import datetime, timedelta

class Player(models.Model):
    name = models.CharField('name of the player', max_length=100)
    email = models.EmailField()

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name

class SingleRanking(models.Model):
    player = models.ForeignKey('Player', related_name='player', unique=True)
    points = models.FloatField(default=None, null=True)

    @staticmethod
    def findOrCreate(pl):
        try:
            return SingleRanking.objects.get(player=pl)
        except SingleRanking.DoesNotExist:
            new = SingleRanking(player=pl)
            new.save()
            return new

class DoubleRanking(models.Model):
    first_player = models.ForeignKey('Player', related_name='first_player')
    second_player = models.ForeignKey('Player', related_name='second_player')
    points = models.FloatField(default=None, null=True)

    class Meta:
        unique_together = (('first_player', 'second_player'),)

    def __unicode__(self):
        names = []
        names.append(self.first_player.name)
        names.append(self.second_player.name)
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
            new.save()
            return new

class Game(models.Model):
    team_a_1 = models.ForeignKey('Player', related_name='team_a_1')
    team_a_2 = models.ForeignKey('Player', related_name='team_a_2', null=True)
    team_b_1 = models.ForeignKey('Player', related_name='team_b_1')
    team_b_2 = models.ForeignKey('Player', related_name='team_b_2', null=True)
    game_time = models.DateTimeField(auto_now_add=True)
    score_a = models.IntegerField()
    score_b = models.IntegerField()
    score_base = models.IntegerField(choices=(('11', '11'), ('21', '21'))) # 11 or 21

    def __unicode__(self):
        return "%s vs. %s" % (
            self.team_a_1.name if self.team_a_2 == None else "%s & %s" % (self.team_a_1.name, self.team_a_2.name),
            self.team_b_1.name if self.team_b_2 == None else "%s & %s" % (self.team_b_1.name, self.team_b_2.name),
            )

    def isDouble(self):
        return self.team_a_2 and self.team_b_2

def computePoints():
    # Select all the games for the last month
    all_games = Game.objects.filter(game_time__gte=datetime.now()-timedelta(days=30))

    single_acc = {}
    double_acc = {}

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
            __setAccPoints(
                single_acc,
                SingleRanking.findOrCreate(game.team_a_1),
                SingleRanking.findOrCreate(game.team_b_1),
                points
            )

    pp = {}

    for v in single_acc.itervalues():
        pp.setdefault(v['a'], {'s': 0.0, 'c': 0})
        pp.setdefault(v['b'], {'s': 0.0, 'c': 0})
        pp[v['a']]['s'] += v['s']
        pp[v['a']]['c'] += v['c']
        pp[v['b']]['s'] -= v['s']
        pp[v['b']]['c'] += v['c']

    #reset all scores
    SingleRanking.objects.all().update(points=None)

    for (rank, points) in pp.items():
        rank.points = points['s'] / points['c']
        rank.save()

    pp = {}

    for v in double_acc.itervalues():
        pp.setdefault(v['a'], {'s': 0.0, 'c': 0})
        pp.setdefault(v['b'], {'s': 0.0, 'c': 0})
        pp[v['a']]['s'] += v['s']
        pp[v['a']]['c'] += v['c']
        pp[v['b']]['s'] -= v['s']
        pp[v['b']]['c'] += v['c']

    #reset all scores
    DoubleRanking.objects.all().update(points=None)

    for (rank, points) in pp.items():
        rank.points = points['s'] / points['c']
        rank.save()



class InvalidScore(Exception):
    pass
