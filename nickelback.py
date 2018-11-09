import json
import random
import sys
import time

import spotipy
import spotipy.util as util
#from spotipy.oauth2 import SpotifyClientCredentials

#constants
TARGET_ARTIST = "Nickelback"

#parse arguments
if len(sys.argv) == 2:
    username = sys.argv[1]
else:
    print "Usage: python %s username" % (sys.argv[0],)
    sys.exit()

#determine necessary scope
scope = (
	"user-read-playback-state "
	#+ "user-read-currently-playing "
	#+ "user-modify-playback-state  "	
	+ "streaming "
	#+ "app-remote-control "
	#+ "playlist-read-collaborative "
	#+ "playlist-modify-private  "
	#+ "playlist-modify-public  "
	#+ "playlist-read-private "
	#+ "user-read-birthdate "
	#+ "user-read-email "
	#+ "user-read-private "
	#+ "user-follow-modify "
	#+ "user-follow-read "	
	#+ "user-library-read "
	+ "user-library-modify "
	+ "user-read-recently-played "
	#+ "user-top-read ")
).strip()

#client credentials flow
#client_credentials_manager = SpotifyClientCredentials(client_id='0ebd3ef528a3403dbe9ab44eed6a727a', 
#                                                      client_secret='4a36c9d01a4542c292de20ec90f967bf')
#sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

#authorization code flow
token = util.prompt_for_user_token(username,
	                               scope,
	                               client_id='0ebd3ef528a3403dbe9ab44eed6a727a',
	                               client_secret='4a36c9d01a4542c292de20ec90f967bf',
	                               redirect_uri='http://localhost/')

if token:
    sp = spotipy.Spotify(auth=token)
else:
    print "Can't get token for %s." % username
    sys.exit()

#helper function for matching and output formatting
def propertyToString(s):
	"formats returned JSON property into a string"
	return json.dumps(s).strip().replace('"', '')

#gather initial playback info
currentTrack = sp.current_user_playing_track()
currentTrackURI = propertyToString(currentTrack["item"]["uri"])
currentArtistName = propertyToString(currentTrack["item"]["artists"][0]["name"])
currentArtistURI = propertyToString(currentTrack["item"]["artists"][0]["uri"])
currentArtists = currentTrack["item"]["artists"]
lastTrackURI = ""

while (True):
	if (currentTrackURI != lastTrackURI):
		#check to see if they're listening to the right artist (including features)
		artistMatchInd = False
		for thisArtist in currentArtists:
			if TARGET_ARTIST.lower() == propertyToString(thisArtist["name"]).lower():
				artistMatchInd = True
				break

		if artistMatchInd:
			#they're already playing this artist
			currentSongName = propertyToString(sp.track(currentTrackURI)["name"])

			#determine current track's cut deepness
			cutDeepness = "100+"
			topSongs = sp.search(TARGET_ARTIST, limit=50, offset=0, type='track', market="US")["tracks"]["items"] + \
                       sp.search(TARGET_ARTIST, limit=50, offset=50, type='track', market="US")["tracks"]["items"]
           
			for i in range(len(topSongs) - 1):
				if (currentSongName.lower() == propertyToString(topSongs[i]["name"]).lower()):
					cutDeepness = i + 1
					break

			#add current track to saved songs and make sure we keep playing Nickelback
			sp.current_user_saved_tracks_add(tracks=[ currentTrackURI ])
			lastTrackURI = currentTrackURI

			print "Nice, brother... you're listening to %s.\n" % TARGET_ARTIST, \
			      "Added %s (cut_deepness=%s) to your saved songs." % (currentSongName, cutDeepness)

		else:
			print "Woah, brother, looks like you're listening to %s.\n" % currentArtistName, \
			      "Let's get you jamming to some %s..." % TARGET_ARTIST

			#pause current track and find a better song
			sp.pause_playback(device_id=None)

			cutDeepness = random.randrange(99)
			newSong = sp.search(TARGET_ARTIST, limit=1, offset=cutDeepness, type='track', market="US")["tracks"]["items"][0]
			newTrackName = propertyToString(newSong["name"])
			newTrackURI = propertyToString(newSong["uri"])
			newSongArtistURI = propertyToString(newSong["artists"][0]["uri"])

			print "This looks better... %s (cut_deepness=%d)!\n" % (newTrackName, cutDeepness), \
			      "Don't worry, already added this to your saved songs."

			#play the better song and add it to their saved songs
			sp.repeat(state="off")
			sp.start_playback(uris=[ newTrackURI ])
			sp.current_user_saved_tracks_add(tracks=[ newTrackURI ])
			lastTrackURI = newTrackURI
	else:
		#same song -- has it stopped playing?
		if not sp.current_playback()["is_playing"]:
			#start playing some more of the target artist
			print "Song finished -- let's kick off some more %s." % TARGET_ARTIST
			sp.start_playback(context_uri=currentArtistURI)

	#wait 5 seconds
	time.sleep(5)

	#gather current track
	currentTrack = sp.current_user_playing_track()
	currentTrackURI = propertyToString(currentTrack["item"]["uri"])
	currentArtistName = propertyToString(currentTrack["item"]["artists"][0]["name"])
	currentArtistURI = propertyToString(currentTrack["item"]["artists"][0]["uri"])
	currentArtists = currentTrack["item"]["artists"]





