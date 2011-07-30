from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from client.models import Player, Game, computePoints
import logging

def home(request):
    all_players = Player.objects.all().order_by('-points')
    best_players = all_players[0:3]
    rest_players = all_players[3:]
    return render_to_response('pages/index.html', {
        'best_players': best_players,
        'rest_players': rest_players,
    })

def newgame(request):
    from client.forms import NewGameForm

    if request.method == 'POST': # If the form has been submitted...
        form = NewGameForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            data = form.cleaned_data
            game = Game()
            game.team_a_1 = data['team_a'][0]
            game.team_b_1 = data['team_b'][0]
            if len(data['team_a']) == 2:
                game.team_a_2 = data['team_a'][1]
                game.team_b_2 = data['team_b'][1]
            game.score_base = data['base']
            game.score_a = data['score_a']
            game.score_b = data['score_b']
            game.save()

            return HttpResponseRedirect('/') # Redirect after POST
    else:
        form = NewGameForm() # An unbound form

    return render_to_response(
        'pages/newgame.html', {
            'form': form,
        },
        context_instance=RequestContext(request)
    )
    
def game(request, game_id):
    return HttpResponse(Game.objects.get(id=game_id))

def update(request):
    computePoints()
    return HttpResponseRedirect('/')
