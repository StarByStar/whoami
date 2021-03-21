from django.conf import settings
from django.db import models
from django.utils import timezone
from datetime import datetime
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

# Create your models here.

class Game(models.Model):
	creator_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)
	name = models.CharField(max_length=30)
	password = models.CharField(max_length=30)
	start_date = models.DateTimeField(default=timezone.now)
	end_date = models.DateTimeField(blank=True, null=True)
	game_state = models.CharField(max_length=30)


	# get all current players
	def get_players(self):
		players = Player.objects.filter(game_id=self.pk)
		return players


	# add player to the game
	def assign(self):
		players = self.get_players()
		players_list = list()
		i = 0
		#create player list
		for player in players:
			players_list.append(player.userid)
		# odd players
		if len(players_list) % 2 == 0:
			players_list.reverse()
			for player in players:
				player.whoassign = User.objects.get(username=players_list[i])
				player.save()
				i += 1
		else: # even players
			players_list.append(players_list[len(players_list)-1])
			players_list.reverse()
			for player in players:
				player.whoassign = User.objects.get(username=players_list[i])
				player.save()
				i += 1

class Player(models.Model):
	game_id = models.ForeignKey('Game', on_delete=models.CASCADE)
	userid = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="player")
	character = models.CharField(max_length=30, blank=True, null=True)
	whoassign = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="player_who_assign", null = True, blank=True)

	def set_character():
		pass


	# need to assign?
	def need_to_assign(self, game_id):
		try:
			need_to_assign = Player.objects.filter(game_id=game_id, whoassign=self.userid)
		except ObjectDoesNotExist:
			return False
		else:
			for player in need_to_assign:
				if player.character is None:
					return True
				else:
					return False
			return False
