from django.conf import settings
from django.db import models
from django.utils import timezone
from datetime import datetime
#from django.contrib.auth.models import User
# Create your models here.

class Game(models.Model):
	creator_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)
	name = models.CharField(max_length=30)
	password = models.CharField(max_length=30)
	start_date = models.DateTimeField(default=timezone.now)
	end_date = models.DateTimeField(blank=True, null=True)
	game_state = models.CharField(max_length=30)


	# get all current players
	def get_players():
		players = Player.objects.filter(game_id=obj.pk)
		return players

	# add player to the game
	def join_game():
		pass


class Player(models.Model):
	game_id = models.ForeignKey('Game', on_delete=models.CASCADE)
	userid = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	character = models.CharField(max_length=30, blank=True, null=True)

	def set_character():
		pass