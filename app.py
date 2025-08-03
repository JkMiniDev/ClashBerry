import os
import json
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configuration
COC_API_TOKEN = os.getenv("API_TOKEN")
COC_API_BASE = "https://cocproxy.royaleapi.dev/v1"

# Load emoji mappings
def load_emoji_data():
    emoji_data = {}
    emoji_files = {
        'town_halls': 'commands/emoji/town_halls.json',
        'league': 'commands/emoji/league.json',
        'cwl_league': 'commands/emoji/cwl_league.json',
        'capital_hall': 'commands/emoji/capital_hall.json'
    }
    
    for name, path in emoji_files.items():
        try:
            with open(path, 'r') as f:
                emoji_data[name] = json.load(f)
        except FileNotFoundError:
            emoji_data[name] = {}
    
    return emoji_data

EMOJI_DATA = load_emoji_data()

def get_clan_data(clan_tag):
    """Fetch clan data from COC API"""
    if not clan_tag.startswith('#'):
        clan_tag = '#' + clan_tag
    
    url = f"{COC_API_BASE}/clans/{clan_tag.replace('#', '%23')}"
    headers = {"Authorization": f"Bearer {COC_API_TOKEN}"}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error fetching clan data: {e}")
        return None

def get_player_data(player_tag):
    """Fetch player data from COC API"""
    if not player_tag.startswith('#'):
        player_tag = '#' + player_tag
    
    url = f"{COC_API_BASE}/players/{player_tag.replace('#', '%23')}"
    headers = {"Authorization": f"Bearer {COC_API_TOKEN}"}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error fetching player data: {e}")
        return None

def get_clan_war_data(clan_tag):
    """Fetch current clan war data"""
    if not clan_tag.startswith('#'):
        clan_tag = '#' + clan_tag
    
    url = f"{COC_API_BASE}/clans/{clan_tag.replace('#', '%23')}/currentwar"
    headers = {"Authorization": f"Bearer {COC_API_TOKEN}"}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error fetching war data: {e}")
        return None

def get_cwl_data(clan_tag):
    """Fetch CWL group data"""
    if not clan_tag.startswith('#'):
        clan_tag = '#' + clan_tag
    
    url = f"{COC_API_BASE}/clans/{clan_tag.replace('#', '%23')}/currentwar/leaguegroup"
    headers = {"Authorization": f"Bearer {COC_API_TOKEN}"}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error fetching CWL data: {e}")
        return None

@app.route('/')
def index():
    """Main landing page"""
    return render_template('index.html')

@app.route('/commands')
def commands():
    """Discord commands showcase page"""
    discord_commands = [
        {
            'name': '!clan',
            'description': 'Display comprehensive clan information including member list, war stats, and clan details',
            'usage': '!clan <clan_tag>',
            'features': ['Clan overview', 'Member list with TH levels', 'War statistics', 'Clan type and requirements']
        },
        {
            'name': '!player',
            'description': 'Show detailed player statistics, achievements, and troop information',
            'usage': '!player <player_tag>',
            'features': ['Player stats', 'Achievement progress', 'Troop levels', 'Clan information']
        },
        {
            'name': '!war',
            'description': 'Display current clan war information with attack details and member performance',
            'usage': '!war <clan_tag>',
            'features': ['War overview', 'Attack progress', 'Member performance', 'Star and destruction percentages']
        },
        {
            'name': '!linkaccount',
            'description': 'Link your Discord account to your Clash of Clans player tag',
            'usage': '!linkaccount <player_tag>',
            'features': ['Account verification', 'Discord-COC linking', 'Profile management']
        },
        {
            'name': '!addclan',
            'description': 'Add a clan to the server\'s tracking system',
            'usage': '!addclan <clan_tag>',
            'features': ['Clan registration', 'Server clan list', 'Clan monitoring']
        },
        {
            'name': '!accounts',
            'description': 'View all linked accounts for a Discord user',
            'usage': '!accounts [@user]',
            'features': ['Account overview', 'Verification status', 'Multiple account support']
        }
    ]
    return render_template('commands.html', commands=discord_commands)

@app.route('/clan')
def clan_search():
    """Clan search and display page"""
    clan_tag = request.args.get('tag', '')
    clan_data = None
    war_data = None
    cwl_data = None
    
    if clan_tag:
        clan_data = get_clan_data(clan_tag)
        if clan_data:
            war_data = get_clan_war_data(clan_tag)
            cwl_data = get_cwl_data(clan_tag)
    
    return render_template('clan.html', 
                         clan_data=clan_data, 
                         war_data=war_data,
                         cwl_data=cwl_data,
                         emoji_data=EMOJI_DATA,
                         search_tag=clan_tag)

@app.route('/player')
def player_search():
    """Player search and display page"""
    player_tag = request.args.get('tag', '')
    player_data = None
    
    if player_tag:
        player_data = get_player_data(player_tag)
    
    return render_template('player.html', 
                         player_data=player_data,
                         emoji_data=EMOJI_DATA,
                         search_tag=player_tag)

@app.route('/api/clan/<clan_tag>')
def api_clan(clan_tag):
    """API endpoint for clan data"""
    clan_data = get_clan_data(clan_tag)
    if clan_data:
        return jsonify(clan_data)
    return jsonify({'error': 'Clan not found'}), 404

@app.route('/api/player/<player_tag>')
def api_player(player_tag):
    """API endpoint for player data"""
    player_data = get_player_data(player_tag)
    if player_data:
        return jsonify(player_data)
    return jsonify({'error': 'Player not found'}), 404

@app.route('/api/war/<clan_tag>')
def api_war(clan_tag):
    """API endpoint for war data"""
    war_data = get_clan_war_data(clan_tag)
    if war_data:
        return jsonify(war_data)
    return jsonify({'error': 'War data not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)