from django.shortcuts import render
from .rpsls_game import *

menu = [{'title': 'GW2-TP', 'url_name': 'alert'},
        {'title': 'RPSLS-game', 'url_name': 'rpsls_game'},
        ]


def rpsls_game(request):
    if request.method == 'POST':
        choice = request.POST.get('choice')

        opponent = request.session.get('opponent')
        request.session['opponent'] = opponent

        round_counter = request.session.get('round_counter', 1)
        round_counter += 1
        request.session['round_counter'] = round_counter

        computer_fighter = computer_choice(opponent, 'Rock')
        request.session['computer_fighter'] = computer_fighter

        player_score = request.session.get('player_score', 0)
        request.session['player_score'] = player_score

        computer_score = request.session.get('computer_score', 0)
        request.session['computer_score'] = computer_score

        if choice == 'new_game':

            opponent = computer_opponent()
            request.session['opponent'] = opponent

            round_counter = 1
            request.session['round_counter'] = round_counter

            player_score = 0
            request.session['player_score'] = player_score

            computer_score = 0
            request.session['computer_score'] = computer_score

        winner = who_won(choice, computer_fighter)
        if winner == 'player_win':
            player_score += 1
            request.session['player_score'] = player_score
        elif winner == 'computer_win':
            computer_score += 1
            request.session['computer_score'] = computer_score

        return render(request, 'rpsls/rpsls.html',
                      {'menu': menu,
                       'title': 'RPSLS-game',
                       'choice': choice,
                       'round_counter': round_counter,
                       'opponent': opponent,
                       'player_score': player_score,
                       'computer_score': computer_score,
                       'computer_fighter': computer_fighter,
                       'winner': winner})

    opponent = computer_opponent()
    request.session['opponent'] = opponent

    # 'Rock' - вместо этого должен быть "choice",
    # что бы мог сыграть Локки, но пока это не работает
    computer_fighter = computer_choice(opponent, 'Rock')
    request.session['computer_fighter'] = computer_fighter

    choice = 'new_game'
    round_counter = 1
    request.session['round_counter'] = round_counter
    player_score = 0
    request.session['player_score'] = player_score
    computer_score = 0
    request.session['computer_score'] = computer_score
    return render(request, 'rpsls/rpsls.html',
                  {'menu': menu,
                   'title': 'RPSLS-game',
                   'opponent': opponent,
                   'choice': choice,
                   'round_counter': round_counter,
                   'player_score': player_score,
                   'computer_score': computer_score,
                   'computer_fighter': computer_fighter})
