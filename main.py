#TODO: show which character was used
#TODO: show leaderboard based on argument1 which is starting point

from supabase import create_client, Client
from warnings import filterwarnings
import scratchattach as sa
from dotenv import load_dotenv
import os

load_dotenv()

filterwarnings('ignore', category=sa.LoginDataWarning)

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE")
session_id = os.getenv("SCRATCH_SESSION_ID")

if url is None or key is None:
    raise ValueError("Supabase URL and KEY must be set in environment variables.")
if session_id is None:
    raise ValueError("SESSION_ID must be set in environment variables.")

session = sa.login_by_id(session_id, username="SupKittyMeow")
cloud = session.connect_cloud("1175964459")
client = cloud.requests()

supabase: Client = create_client(url, key)

@client.event
def on_ready(): # just to make sure everything is working
    print("Request handler is running")

@client.request
def ping(): # sends back 'pong' to the Scratch project
    return "pong"

@client.request
def add_score(argument1, argument2): # sets the score of the user to the second argument, saved to a database
    data = {"Username": argument1, "Max kills": argument2}
    supabase.table("leaderboard").upsert(data).execute()
    return "score set"

@client.request
def get_score(argument1): # retrieve a user's score
    response = supabase.table("leaderboard").select("*").eq("Username", argument1).execute() 
    # Check if the player exists in the leaderboard
    if response.data:
        # If player exists, return the data
        return int(response.data[0].get("Max kills", 0))
    else:
        # If player doesn't exist, return 0
        return 0
    
@client.request
def reset_score(argument1): # deletes the user's score from the database
    supabase.table("leaderboard").delete().eq("Username", argument1).execute()
    return "RESET"

@client.request
def get_leaderboard(leaderboardStart): # returns a list of the top 10 scores
    leaderboardStart = int(leaderboardStart)
    response = (
        supabase
        .table("leaderboard")
        .select('"Username","Max kills"')
        .order('"Max kills"', desc=True)
        .order("Username", desc=False)
        .range(leaderboardStart, leaderboardStart + 4)
        .execute()
    )

    # Get total count of rows (excluding header, if you have one as a row)
    count_response = supabase.table("leaderboard").select("Username", count="exact").execute() #type: ignore
    total_players = count_response.count or 0

    if response.data:
        leaderboard_list = [
            f"{item['Username']}: {item['Max kills']}" for item in response.data
        ]
        leaderboard_list.append(str(total_players))
        return leaderboard_list
    else:
        return []

client.start(thread=True)