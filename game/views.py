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


@login_required(login_url='/login')
def new_game(request):
	return render(request, 'game/new_game.html')


@login_required(login_url='/login')
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
@login_required(login_url='/login')
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


@login_required(login_url='/login')
def lobby(request, pk):
	context = {}
	current_game = Game.objects.get(pk=pk)
	# if game already close:
	if current_game.game_state == 'close':
		return redirect('/')
	else:
		current_user = request.user
		user_id = current_user.id
		context['game_name'] = current_game.name
		context['game_id'] = current_game.pk
		gamers = ''
		try: 
			current_player = Player.objects.get(userid=request.user, game_id=current_game.pk)
		except ObjectDoesNotExist:
			return redirect('/find_game/')
		context['players'] = players_for_lobby(current_game, request)
		context['state'] = current_game.game_state
		context['need_to_assign'] = current_player.need_to_assign(current_game.pk)

		# diable or enable start-close btn
		if str(current_game.creator_id) == str(current_user.get_username()):
			context['creator'] = True # draw btn if creator
		else:
			context['creator'] = False

		try:
			god_gamer = Player.objects.get(game_id=pk, userid=user_id)
		except ObjectDoesNotExist:
			return redirect('/find_game/')
		else:
			return render(request, 'game/lobby.html', context)

# get players, characters (with form)
def players_for_lobby(game, request):
	players = game.get_players()
	gamers = '<table class="game_table">'
	if game.game_state == 'lobby':
		for player in players:
			gamers += f'<tr><td>{player.userid}</td></tr>'
	else:
		for player in players:
			if str(player.whoassign) == str(request.user.username):
				if player.character is None:
					gamers += f'<tr><td>{player.userid}</td><input type="hidden" name="player" required value={player.userid}><input type="hidden" name="game_id" required value={game.pk}><td><input type="text" name="character" required></td></tr>'
				else:
					gamers += f'<tr><td>{player.userid}</td><td>{player.character}</td></tr>'
			else:
				if str(player.userid) == str(request.user.username):
						if player.character is None:
							gamers += f'<tr><td>{player.userid}</td><td>Didnt set yet</td></tr>'
						else:
							gamers += f'<tr><td>{player.userid}</td><td>?????</td></tr>'	
				else:
					if player.character is None:
						gamers += f'<tr><td>{player.userid}</td><td>Didnt set yet</td></tr>'
					else:
						gamers += f'<tr><td>{player.userid}</td><td>{player.character}</td></tr>'
	gamers += '</table>'
	return gamers	

# def char_form():
#  form = f'<form method="POST" action="/start_game/"> '
# 		f'{% csrf_token %} '
# 		f'<input type="text" required name="player_character"> '
# 		f' <input type="submit" value="set character"> '
# 		f'</form>'

@login_required
def set_character(request):
	if request.method == 'POST':
		game_id = request.POST['game_id']
		whom = request.POST['player']
		character = request.POST['character']
		user = User.objects.get(username=whom)
		player_obj = Player.objects.get(game_id=game_id, userid=user.id)
		if str(player_obj.whoassign) == str(request.user.username):
			player_obj.character = character
			player_obj.save()


	return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))




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
	choosen_game = Game.objects.get(pk=game_id)
	if choosen_game.game_state == 'lobby':
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
    		try: # player already exist?
    			god_gamer = Player.objects.get(game_id=game_id, userid=user_id)
    		except ObjectDoesNotExist: # no
	    		add_player(game_id, user_id)
	    		lobby_url = '/lobby/' + str(game_id) + '/'
	    		return redirect(lobby_url) # to lobby
	    	else: # yes
	    		lobby_url = '/lobby/' + str(game_id) + '/'
	    		return redirect(lobby_url) # to lobby
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


@login_required(login_url='/login')
def start_game(request):
	if request.method == 'POST':
		game_id = request.POST['game_id']
		current_game = Game.objects.get(pk=game_id)
		#if  current_game.game_state == 'lobby':
		if str(request.user.username) == str(current_game.creator_id) and current_game.game_state == 'lobby':
			current_game.game_state = 'active'
			current_game.assign()
			current_game.save()
			return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
		elif str(request.user.username) == str(current_game.creator_id) and current_game.game_state == 'active':
			current_game.game_state = 'close'
			current_game.save()
			return redirect('/')
	else:
		return HttpResponse(f'something goes wrong')
