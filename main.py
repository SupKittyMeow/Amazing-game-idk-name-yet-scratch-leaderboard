# TODO: show which character was used
# TODO: show leaderboard based on argument1 which is starting point

from warnings import filterwarnings
from upstash_redis import Redis
import scratchattach as sa
from dotenv import load_dotenv
import os

load_dotenv()

redis = Redis.from_env()

filterwarnings('ignore', category=sa.LoginDataWarning)

session = sa.login_by_id(str(os.getenv("SCRATCH_SESSION_ID")), username="SupKittyMeow")
cloud = session.connect_cloud("1175964459")
client = cloud.requests()

@client.event
def on_ready(): # just to make sure everything is working
    print("Request handler is running", flush=True)
    if redis.ping() == "PONG":
        print("Redis is running!", flush=True)

@client.request
def ping(): # sends back 'pong' to the Scratch project
    return "pong"

@client.request
def add_score(argument1, argument2): # sets the score of the user to the second argument, saved to a database
    try:
        score = int(argument2)
    except ValueError:
        return "Error: Score must be a number!"
    
    redis.zadd('leaderboard', {argument1: score} )
    return "score set"

@client.request
def get_score(argument1): # retrieve a user's score
    response = redis.zscore('leaderboard', argument1)

    # Check if the player exists in the leaderboard
    if response is not None:
        # If player exists, return the data
        return int(response)
    else:
        # If player doesn't exist, return 0
        return 0
    
@client.request
def reset_score(argument1): # deletes the user's score from the database
    redis.zrem('leaderboard', argument1)
    return "RESET"

@client.request
def get_leaderboard(leaderboardStart): # returns a list of the top 10 scores
    leaderboardStart = int(leaderboardStart)

    descending_users = redis.zrange('leaderboard', leaderboardStart, leaderboardStart + 4, withscores=True, rev=True)
    
    if descending_users is not None:
        leaderboard_list = [ f"{user[0]}: {int(user[1])}" for user in descending_users ]
        leaderboard_list.append(str(redis.zcard('leaderboard')))
        return leaderboard_list
    else:
        return []

client.start(thread=True)