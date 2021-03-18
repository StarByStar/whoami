from django.shortcuts import render, redirect
from django.contrib import auth
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from game.models import Game, Player
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist


# static main page
def main(request):
	return render(request, 'game/index.html')


def rules(request):
	return render(request, 'game/rules.html')


def about(request):
	return render(request, 'game/about.html')


@login_required(login_url='/admin/login')
def new_game(request):
	return render(request, 'game/new_game.html')


@login_required(login_url='/admin/login')
def find_game(request):
	#return HttpResponse(get_available_games())
	all_games = '<p> Choose your game: </p>'
	available_games = get_available_games()
	for game in available_games:
		all_games +=  (f'<input type="radio" name="chosen_game"'
			f' required value="{game["id"]}">{game["name"]} <br>')
	all_games += (f'<p>Enter password:</p>'
		f'<input type = "password" name="password" required> </br>')
	context = {
		'games': all_games,
	}
	return render(request, 'game/find_game.html', context)


# Create new lobby
@login_required(login_url='/admin/login')
def create_lobby(request):
	context = {}
	if request.method == 'POST':
		name = request.POST['game_name']
		password = request.POST['game_password']
	game = create_game(request, name, password)
	url = 'lobby' + '/' + str(game.pk)
	return redirect(f'/{url}/')


# Create new game object
def create_game(request, game_name, game_password):
	current_user = request.user
	user_id = current_user.id
	start_date = datetime.now()
	game = Game.objects.create(creator_id=current_user, name=game_name, password=game_password, game_state="lobby", start_date=start_date)
	game.save()
	# add creator to plyer list
	add_player(game.pk, user_id)
	# delete old games
	close_old_games()
	return game


@login_required(login_url='/admin/login')
def lobby(request, pk):
	context = {}
	current_game = Game.objects.get(pk=pk)
	current_user = request.user
	user_id = current_user.id
	context['game_name'] = current_game.name
	try:
		god_gamer = Player.objects.get(game_id=pk, userid=user_id)
	except ObjectDoesNotExist:
		return redirect('/find_game/')
	else:
		return render(request, 'game/lobby.html', context)


# Get all available games
def get_available_games():
	games_list = []
	game_dict = {}
	available_games = Game.objects.filter(game_state__iexact='lobby')
	for game in available_games:
		game_dict = {'id': game.id, 'name': game.name }
		games_list.append(game_dict)
	return games_list


# add player to the game
def add_player(game_id, userid):
	new_player = Player.objects.create(
		game_id=Game.objects.get(pk=game_id),
		userid=User.objects.get(id=userid))
	new_player.save()


# add player to existing game
def join_lobby(request):
    if request.method == 'POST':
    	game_id = request.POST['chosen_game']
    	password = request.POST['password']
    	current_user = request.user
    	user_id = current_user.id
    	if check_passwd(game_id, password):
    		try:
    			god_gamer = Player.objects.get(game_id=game_id, userid=user_id)
    		except ObjectDoesNotExist: 
	    		add_player(game_id, user_id)
	    		return HttpResponse('success') # to lobby and create
	    	else:
	    		return HttpResponse('Error. Player already joined') # to lobby
    	return HttpResponse('wrong password') # to error


# validate game password
def check_passwd(game_id, password):
	game = Game.objects.get(id=game_id)
	return game.password == password


# delete games older than 24h
def close_old_games():
	end_date = datetime.now() - timedelta(days=1)
	old_games = Game.objects.filter(start_date__lte=end_date)
	for game in old_games:
		game.end_date = datetime.now()
		game.game_state = 'close'
		game.save()
