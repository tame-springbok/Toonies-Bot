import discord
from discord.ext import commands
import re
import csv
import requests
from urllib.parse import urlencode
import webbrowser

DISCORD_BOT_TOKEN = ''
# Sage: input the channel ID below, no quotes -erase me-
CHANNEL_ID = 1223638165617770572

SPOTIFY_CLIENT_ID = ''
SPOTIFY_CLIENT_SECRET = ''
SPOTIFY_PLAYLIST_ID = ''
SPOTIFY_REDIRECT_URI = 'https://example.com/callback'
SPOTIFY_ACCESS_TOKEN = ''
SPOTIFY_ACCESS_CODE = ''

# Discord bot setup
intents = discord.Intents.all()
intents.messages = True
client = commands.Bot(command_prefix="!", intents=intents)

authorization_url = f"https://accounts.spotify.com/authorize?client_id={SPOTIFY_CLIENT_ID}&response_type=code&redirect_uri={SPOTIFY_REDIRECT_URI}&scope=playlist-modify-public%20playlist-modify-private"

import base64

@client.event
async def on_ready():
    print('Logged in as', client.user)
    channel = client.get_channel(CHANNEL_ID)
    if not channel:
        print(f"Channel with ID {CHANNEL_ID} not found.")
        return
    await channel.send("Hello! Toonies bot is ready!")

@client.command()
async def search_history(ctx):
    channel = client.get_channel(CHANNEL_ID)
    if not channel:
        await ctx.send(f"Channel with ID {CHANNEL_ID} not found.")
        return
    
    # Process channel history
    spotify_links = []
    async for message in channel.history(limit=None):
        links = re.findall(r'https://open.spotify.com/(track|album)/([a-zA-Z0-9]+)', message.content)
        spotify_links.extend(links)

    if spotify_links:
        # Add Spotify links to CSV
        for link_type, link_id in spotify_links:
            add_to_csv(link_type, link_id)
        
        # Send a message indicating that the CSV has been updated
        await ctx.send("Spotify links have been added to the CSV.")
        
        # Send the CSV file as a Discord message
        await send_csv(channel, ctx)

@client.command()
async def add_to_playlist(ctx):
    global SPOTIFY_ACCESS_TOKEN
    try:
        with open('spotify_links.csv', 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                link_type, link_id = row
                response = add_to_spotify_playlist(link_type, link_id, SPOTIFY_ACCESS_TOKEN)    # get response after running
        if response == 200:                                                                     # check the response
            await ctx.send("Tracks and albums have been added to the playlist.")
    except Exception as e:
        await ctx.send(f"An error occurred while adding tracks to the playlist: {e}")

def add_to_spotify_playlist(link_type, link_id, access_token):
#    token = get_spotify_access_token() # doing this by just calling the global
    if access_token:
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        url = f'https://api.spotify.com/v1/playlists/{SPOTIFY_PLAYLIST_ID}/tracks'
        data = {
            'uris': [f'spotify:{link_type}:{link_id}']
        }
        response = requests.post(url, headers=headers, json=data).json() # added .json() because Spotify's API is JSON based, so your data needs to be a valid json data.
        print(f'DEBUG: Response = {response}')
        if response.status_code == 201:
            print(f'Added {link_type} {link_id} to playlist.')
        else:
            print(f'Error: Failed to add {link_type} {link_id} to playlist. Status code: {response.status_code}\n\
                  DEBUG: access_token = {access_token}')
            raise Exception(f"Failed to add {link_type} {link_id} to playlist. Status code: {response.status_code}")
    else:
        raise Exception("Failed to obtain Spotify access token.")
'''
def get_spotify_access_token():
    global SPOTIFY_ACCESS_TOKEN
    print(f'DEBUG: here\'s your token boss: {SPOTIFY_ACCESS_TOKEN}')
    if SPOTIFY_ACCESS_TOKEN:
        # Exchange authorization code for access token
        token_url = 'https://accounts.spotify.com/api/token'
        data = {
            'grant_type': 'SPOTIFY_ACCESS_TOKEN',
            'code': SPOTIFY_ACCESS_TOKEN,
            'redirect_uri': SPOTIFY_REDIRECT_URI,
            'client_id': SPOTIFY_CLIENT_ID,
            'client_secret': SPOTIFY_CLIENT_SECRET,
            'scope': 'playlist-modify-public'
        }
        response = requests.post(token_url, data=data)
        print(f'DEBUG: Status code = {response.status_code}')
        if response.status_code == 200:
            access_token = response.json()['access_token']
            await ctx.send(f'Access Token: {access_token}')
        else:
            await ctx.send('Failed to obtain access token.')
    else:
        await ctx.send('Authorization code not set. Please use !set_token <code> to set the authorization code.')
'''
        
@client.command()
async def set_token(ctx, code):
    global SPOTIFY_ACCESS_TOKEN
    SPOTIFY_ACCESS_TOKEN = code
    await ctx.send(f'Authorization token set successfully!')
    print(f'DEBUG: End of set_token with access token \'{SPOTIFY_ACCESS_TOKEN}\'')

@client.command()
async def set_code(ctx, code):
    global SPOTIFY_ACCESS_CODE
    SPOTIFY_ACCESS_CODE = code
    await ctx.send(f'Authorization code set successfully!')
    print(f'DEBUG: End of set_code with access token \'{SPOTIFY_ACCESS_CODE}\'')

@client.command()
async def get_code(ctx):
    # global SPOTIFY_ACCESS_TOKEN
    # print(f'DEBUG: entered get_token() with access token \'{SPOTIFY_ACCESS_TOKEN}\'')
    if True: # REDUNDANT: always true, the 'else' below will never be reached.
        code_url = 'https://accounts.spotify.com/authorize?'
        auth_headers = {
            #'grant_type': SPOTIFY_ACCESS_TOKEN,
            'response_type': 'code',
            'redirect_uri': SPOTIFY_REDIRECT_URI,
            'client_id': SPOTIFY_CLIENT_ID,
            'client_secret': SPOTIFY_CLIENT_SECRET,
            'scope': 'playlist-modify-public playlist-modify-private'
        }    
        webbrowser.open("https://accounts.spotify.com/authorize?" + urlencode(auth_headers))
        print("DEBUG: Completed webbrowser.open(\"https://accounts.spotify.com/authorize?\" + urlencode(auth_headers))")
        '''
        response = requests.post(token_url, data=data)
        print(f'DEBUG: Status code = {response.status_code}, JSON returned = {response}')
        if response.status_code == 200:
            access_token = response.json()['access_token']
            await ctx.send(f'Access Token: {access_token}')
        else:
            await ctx.send('Failed to obtain access token.')
        '''
    else:
        await ctx.send('Authorization code not set. Please use !set_token <code> to set the authorization code.')
    
@client.command()
async def get_token(ctx):
    encoded_credentials = base64.b64encode(SPOTIFY_CLIENT_ID.encode() + b':' + SPOTIFY_CLIENT_SECRET.encode()).decode("utf-8")

    token_headers = {
        "Authorization": "Basic " + encoded_credentials,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    token_data = {
        "grant_type": "authorization_code",
        "code": SPOTIFY_ACCESS_CODE,
        "redirect_uri": SPOTIFY_REDIRECT_URI
    }

    r = requests.post("https://accounts.spotify.com/api/token", data=token_data, headers=token_headers)
    token = r.json()["access_token"]

    print(f'Token is {token}')
    await ctx.send(f'Your token is `{token}`')

@client.command()
async def authorize(ctx):
    await ctx.send(f"Authorize the bot by visiting the following URL and grant access: {authorization_url}")



# Function to add Spotify links to a CSV file
def add_to_csv(link_type, link_id):
    with open('spotify_links.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([link_type, link_id])

# Function to send the CSV file as a Discord message
async def send_csv(channel, ctx):
    with open('spotify_links.csv', 'rb') as csvfile:
        await channel.send(file=discord.File(csvfile, 'spotify_links.csv'))

# Replace 'YOUR_DISCORD_BOT_TOKEN' with your actual Discord bot token
client.run(DISCORD_BOT_TOKEN)