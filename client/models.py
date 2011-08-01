from django.db import models
from datetime import datetime, timedelta

class Player(models.Model):
    name = models.CharField('name of the player', max_length=100)
    email = models.EmailField()
    points = models.FloatField('total points of the player')

    def __unicode__(self):
        return self.name

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

    all_players = Player.objects.all()

    acc = {}

    def __setAccPoints(a, b, p):
        if (a.id > b.id):
            (a, b) = (b, a)
            p = -p
        k = '%0u-%0u' % (a.id, b.id)
        i = acc.setdefault(k, {'a':a, 'b':b, 's': 0.0, 'c': 0})
        i['s'] += p
        i['c'] += 1

    for game in all_games:
        if game.team_a_2:
            points = float(game.score_a-game.score_b)/2 #in double, win is divided by 2
            points += points > 0 and 5 or -5 #bonus for winning
            __setAccPoints(game.team_a_1, game.team_b_1, points)
            __setAccPoints(game.team_a_1, game.team_b_2, points)
            __setAccPoints(game.team_a_2, game.team_b_1, points)
            __setAccPoints(game.team_a_2, game.team_b_2, points)
        else:
            points = game.score_a-game.score_b
            points += points > 0 and 10 or -10 #bonus for winning
            __setAccPoints(game.team_a_1, game.team_b_1, points)

    pp = {}

    for v in acc.itervalues():
        pp.setdefault(v['a'].id, 0)
        pp.setdefault(v['b'].id, 0)
        pp[v['a'].id] += v['s'] / v['c']
        pp[v['b'].id] -= v['s'] / v['c']

    for player in all_players:
        player.points = pp.get(player.id, 0.0)
        player.save()
        

class InvalidScore(Exception):
    pass
