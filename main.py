import json
import os
import random
import signal
import sys
import time
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Union

from highrise import BaseBot, Position, User, SessionMetadata, Reaction, CurrencyItem, Item, AnchorPosition

# Функция логирования событий
def log_event(event_type: str, message: str):
    """Логирование событий в файл"""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{event_type}] {message}\n"
        
        with open("bot_log.txt", "a", encoding="utf-8") as f:
            f.write(log_message)
            
        # Выводим в консоль только важные события
        if event_type in ["ERROR", "WARNING", "ADMIN", "MOD"]:
            print(log_message.strip())
    except Exception as e:
        print(f"Error logging event: {e}")

# Глобальные переменные для хранения данных
VIP_USERS = {}  # user_id: {"expires": datetime, "tp_uses": 0, "prank_uses": 0}
BANNED_USERS = {}
MUTED_USERS = {}
USER_HEARTS = {}
USER_ACTIVITY = {}
USER_INFO = {}
USER_NAMES = {}
TELEPORT_POINTS = {}

USER_JOIN_TIMES = {}
MARRIAGES = {}  # user_id: {"partner": partner_id, "date": datetime}
DIVORCE_COUNT = {}  # user_id: {"count": int} - количество разводов
WARNINGS = {}  # user_id: {"count": int, "last_warning": datetime}
USER_LEVELS = {}  # user_id: {"level": int, "messages": int}
MESSAGE_COUNT = {}  # user_id: count
CUSTOM_TP_POINTS = {}  # point_name: {"x": x, "y": y, "z": z, "alternatives": []}
DUEL_REQUESTS = {}  # user_id: {"opponent": opponent_id, "timestamp": datetime}
MARRIAGE_PROPOSALS = {}  # user_id: {"proposer": proposer_id, "timestamp": datetime}
DUEL_LOCATION = {}  # {"x": x, "y": y, "z": z, "facing": facing}
VIP_SAVINGS = {}  # user_id: {"amount": int, "username": str} - накопления для VIP
USER_PROFILES = {}  # user_id: {"username": str, "bio": str, "joined_at": str, "num_followers": int, "num_following": int, "num_friends": int, "country_code": str, "crew": str, "last_seen": str}
BOT_SPAWN_POSITION = {}  # {"x": x, "y": y, "z": z, "facing": facing} - позиция спавна бота
WISHES_SUGGESTIONS = []  # [{"user": str, "username": str, "message": str, "timestamp": str}] - пожелания и предложения

# Боевые анимации для дуэлей
FIGHT_EMOTES = [
    "emote-boxer",  # Ready To Rumble
    "emote-pose3",  # I Challenge You!
    "emote-armcannon",  # emote-armcannon
    "dance-wrong",  # dance-wrong
    "emote-electrified",  # emote-electrified
    "emote-fireworks",  # emote-fireworks
]

# Словарь анимаций (только проверенные бесплатные анимации)
emotes = {
    "1": {"id": "dance-kawai", "name": "Kawaii Go Go", "duration": 10.85, "is_free": True},
    "2": {"id": "emote-hyped", "name": "Hyped", "duration": 7.62, "is_free": True},
    "3": {"id": "emoji-halo", "name": "Levitate", "duration": 6.52, "is_free": True},
    "4": {"id": "idle-hero", "name": "Hero Pose", "duration": 22.33, "is_free": True},
    "5": {"id": "emote-astronaut", "name": "Zero Gravity", "duration": 13.93, "is_free": True},
    "6": {"id": "emote-zombierun", "name": "Zombie Run", "duration": 10.05, "is_free": True},
    "7": {"id": "emote-dab", "name": "Dab", "duration": 3.75, "is_free": True},
    "8": {"id": "emote-snake", "name": "Do The Worm", "duration": 6.63, "is_free": True},
    "9": {"id": "idle-loop-sad", "name": "Bummed", "duration": 21.80, "is_free": True},
    "10": {"id": "idle-loop-happy", "name": "Chillin'", "duration": 19.80, "is_free": True},
    "11": {"id": "emote-kissing", "name": "Sweet Smooch", "duration": 6.69, "is_free": True},
    "12": {"id": "emoji-shush", "name": "Shush", "duration": 3.40, "is_free": True},
    "13": {"id": "idle_tough", "name": "Tough", "duration": 28.64, "is_free": True},
    "14": {"id": "emote-fail3", "name": "Fail", "duration": 7.06, "is_free": True},
    "15": {"id": "emote-receive-disappointed", "name": "Disappointed", "duration": 7.14, "is_free": True},
    "16": {"id": "emote-celebrate", "name": "Party Time!", "duration": 4.35, "is_free": True},
    "17": {"id": "emote-shrink", "name": "Shrink", "duration": 9.99, "is_free": True},
    "18": {"id": "emote-pose10", "name": "Arabesque", "duration": 5.00, "is_free": True},
    "19": {"id": "emote-shy2", "name": "Bashful Blush", "duration": 6.34, "is_free": True},
    "20": {"id": "emote-puppet", "name": "Possessed Puppet", "duration": 17.89, "is_free": True},
    "21": {"id": "emote-headblowup", "name": "Revelations", "duration": 13.66, "is_free": True},
    "22": {"id": "emote-creepycute", "name": "Watch Your Back", "duration": 9.01, "is_free": True},
    "23": {"id": "dance-creepypuppet", "name": "Creepy Puppet", "duration": 7.79, "is_free": True},
    "24": {"id": "dance-anime", "name": "Saunter Sway", "duration": 9.60, "is_free": True},
    "25": {"id": "dance-pinguin", "name": "Groovy Penguin", "duration": 12.81, "is_free": True},
    "26": {"id": "idle-guitar", "name": "Air Guitar", "duration": 14.15, "is_free": True},
    "27": {"id": "emote-boxer", "name": "Ready To Rumble", "duration": 6.75, "is_free": True},
    "28": {"id": "emote-celebrationstep", "name": "Celebration Step", "duration": 5.18, "is_free": True},
    "29": {"id": "emote-pose6", "name": "Big Surprise", "duration": 6.46, "is_free": True},
    "30": {"id": "emote-pose9", "name": "Ditzy pose", "duration": 6.00, "is_free": True},
    "31": {"id": "emote-stargazer", "name": "Stargazing", "duration": 7.93, "is_free": True},
    "32": {"id": "dance-wrong", "name": "Wrong Dance", "duration": 13.60, "is_free": True},
    "33": {"id": "idle-uwu", "name": "UWU Mood", "duration": 25.50, "is_free": True},
    "34": {"id": "emote-fashionista", "name": "Fashionista", "duration": 6.33, "is_free": True},
    "35": {"id": "dance-icecream", "name": "Ice Cream Dance", "duration": 16.58, "is_free": True},
    "36": {"id": "emote-gravity", "name": "Gravity", "duration": 9.02, "is_free": True},
    "37": {"id": "emote-punkguitar", "name": "Punk Guitar", "duration": 10.59, "is_free": True},
    "38": {"id": "idle-dance-tiktok4", "name": "Say So Dance", "duration": 16.55, "is_free": True},
    "39": {"id": "emote-cutey", "name": "I'm A Cutie!", "duration": 4.07, "is_free": True},
    "40": {"id": "emote-pose5", "name": "Fashion Pose", "duration": 5.49, "is_free": True},
    "41": {"id": "emote-pose3", "name": "I Challenge You!", "duration": 5.57, "is_free": True},
    "42": {"id": "emote-pose1", "name": "Flirty Wink", "duration": 4.71, "is_free": True},
    "43": {"id": "idle-dance-casual", "name": "A Casual Dance", "duration": 9.57, "is_free": True},
    "44": {"id": "emote-pose8", "name": "Cheerful", "duration": 5.62, "is_free": True},
    "45": {"id": "emote-pose7", "name": "Embracing Model", "duration": 5.28, "is_free": True},
    "46": {"id": "idle-fighter", "name": "Fighter", "duration": 18.64, "is_free": True},
    "47": {"id": "emote-armcannon", "name": "Arm Cannon", "duration": 8.15, "is_free": True},
    "48": {"id": "emote-electrified", "name": "Electrified", "duration": 12.45, "is_free": True},
    "49": {"id": "emote-fireworks", "name": "Fireworks", "duration": 13.15, "is_free": True},
    "50": {"id": "emote-trampoline", "name": "Trampoline", "duration": 6.11, "is_free": True},
    "51": {"id": "emote-launch", "name": "Launch", "duration": 10.88, "is_free": True},
    "52": {"id": "emote-cutesalute", "name": "Cute Salute", "duration": 3.79, "is_free": True},
    "53": {"id": "emote-salute", "name": "At Attention", "duration": 4.79, "is_free": True},
    "54": {"id": "dance-tiktok11", "name": "Wop Dance", "duration": 11.37, "is_free": True},
    "55": {"id": "dance-employee", "name": "Push It", "duration": 8.55, "is_free": True},
    "56": {"id": "emote-gift", "name": "This Is For You!", "duration": 6.09, "is_free": True},
    "57": {"id": "dance-touch", "name": "Sweet Little Moves", "duration": 13.15, "is_free": True},
    "58": {"id": "sit-relaxed", "name": "Repose", "duration": 31.21, "is_free": True},
    "59": {"id": "emote-sleigh", "name": "Sleigh Ride", "duration": 12.51, "is_free": True},
    "60": {"id": "emote-attention", "name": "Gimme Attention!", "duration": 5.65, "is_free": True},
    "61": {"id": "dance-jinglebell", "name": "Jingle Hop", "duration": 12.09, "is_free": True},
    "62": {"id": "emote-timejump", "name": "Timejump", "duration": 5.51, "is_free": True},
    "63": {"id": "idle-toilet", "name": "Gotta Go!", "duration": 33.48, "is_free": True},
    "64": {"id": "idle-nervous", "name": "Bit Nervous", "duration": 22.81, "is_free": True},
    "65": {"id": "idle-wild", "name": "Scritchy", "duration": 27.35, "is_free": True},
    "66": {"id": "emote-iceskating", "name": "Ice Skating", "duration": 8.41, "is_free": True},
    "67": {"id": "sit-open", "name": "Laid Back", "duration": 27.28, "is_free": True},
    "68": {"id": "emote-howl", "name": "Moonlit Howl", "duration": 8.10, "is_free": True},
    "69": {"id": "idle-howl", "name": "Nocturnal Howl", "duration": 48.62, "is_free": True},
    "70": {"id": "emote-theatrical-test", "name": "Theatrical", "duration": 10.86, "is_free": True},
    "71": {"id": "emote-shocked", "name": "Shocked", "duration": 5.59, "is_free": True},
    "72": {"id": "emote-flirt", "name": "Flirt", "duration": 7.95, "is_free": True},
    "73": {"id": "emote-laugh", "name": "Laugh", "duration": 4.89, "is_free": True},
    "74": {"id": "emote-cry", "name": "Cry", "duration": 6.12, "is_free": True},
    "75": {"id": "emote-sleep", "name": "Sleep", "duration": 8.45, "is_free": True},
    "76": {"id": "emote-wink", "name": "Wink", "duration": 3.21, "is_free": True},
    "77": {"id": "emote-wave", "name": "Wave", "duration": 4.33, "is_free": True},
    "78": {"id": "emote-point", "name": "Point", "duration": 3.67, "is_free": True},
    "79": {"id": "emote-clap", "name": "Clap", "duration": 5.14, "is_free": True},
    "80": {"id": "emote-bow", "name": "Bow", "duration": 4.88, "is_free": True},
    "81": {"id": "dance-tiktok10", "name": "Shuffle Dance", "duration": 9.41, "is_free": True},
    "82": {"id": "idle-dance-tiktok7", "name": "Renegade", "duration": 14.05, "is_free": True},
    "83": {"id": "dance-weird", "name": "Grave Dance", "duration": 22.87, "is_free": True},
    "84": {"id": "dance-tiktok9", "name": "Viral Groove", "duration": 13.04, "is_free": True},
    "85": {"id": "emote-cute", "name": "emote-cute", "duration": 7.20, "is_free": True},
    "86": {"id": "emote-superpose", "name": "Lambi's Pose", "duration": 5.43, "is_free": True},
    "87": {"id": "emote-frog", "name": "Froggie Hop", "duration": 16.14, "is_free": True},
    "88": {"id": "idle_singing", "name": "Sing Along", "duration": 11.31, "is_free": True},
    "89": {"id": "emote-energyball", "name": "Energy Ball", "duration": 8.28, "is_free": True},
    "90": {"id": "emote-maniac", "name": "Maniac", "duration": 5.94, "is_free": True},
    "91": {"id": "emote-swordfight", "name": "Sword Fight", "duration": 7.71, "is_free": True},
    "92": {"id": "emote-teleporting", "name": "Teleport", "duration": 12.89, "is_free": True},
    "93": {"id": "emote-float", "name": "Floating", "duration": 9.26, "is_free": True},
    "94": {"id": "emote-telekinesis", "name": "Telekinesis", "duration": 11.01, "is_free": True},
    "95": {"id": "emote-slap", "name": "Slap", "duration": 4.06, "is_free": True},
    "96": {"id": "emote-frustrated", "name": "Pissed Off", "duration": 6.41, "is_free": True},
    "97": {"id": "emote-embarrassed", "name": "Embarrassed", "duration": 9.09, "is_free": True},
    "98": {"id": "idle-enthusiastic", "name": "Enthused", "duration": 17.53, "is_free": True},
    "99": {"id": "emote-confused", "name": "Confusion", "duration": 9.58, "is_free": True},
    "100": {"id": "dance-shoppingcart", "name": "Let's Go Shopping", "duration": 5.56, "is_free": True},
    "101": {"id": "emote-rofl", "name": "ROFL!", "duration": 7.65, "is_free": True},
    "102": {"id": "emote-roll", "name": "Roll", "duration": 4.31, "is_free": True},
    "103": {"id": "emote-superrun", "name": "Super Run", "duration": 7.16, "is_free": True},
    "104": {"id": "emote-superpunch", "name": "Super Punch", "duration": 5.75, "is_free": True},
    "105": {"id": "emote-kicking", "name": "Super Kick", "duration": 6.21, "is_free": True},
    "106": {"id": "emote-apart", "name": "Falling Apart", "duration": 5.98, "is_free": True},
    "107": {"id": "emote-hug", "name": "Partner Hug", "duration": 4.53, "is_free": True},
    "108": {"id": "emote-secrethandshake", "name": "Secret Handshake", "duration": 6.28, "is_free": True},
    "109": {"id": "emote-peekaboo", "name": "Peekaboo!", "duration": 4.52, "is_free": True},
    "110": {"id": "emote-monster_fail", "name": "Monster Fail", "duration": 5.42, "is_free": True},
    "111": {"id": "dance-zombie", "name": "Zombie Dance", "duration": 13.83, "is_free": True},
    "112": {"id": "emote-ropepull", "name": "Rope Pull", "duration": 10.69, "is_free": True},
    "113": {"id": "emote-proposing", "name": "Proposing", "duration": 5.91, "is_free": True},
    "114": {"id": "emote-sumo", "name": "Sumo Fight", "duration": 11.64, "is_free": True},
    "115": {"id": "emote-charging", "name": "Charging", "duration": 9.53, "is_free": True},
    "116": {"id": "emote-ninjarun", "name": "Ninja Run", "duration": 6.50, "is_free": True},
    "117": {"id": "emote-elbowbump", "name": "Elbow Bump", "duration": 6.44, "is_free": True},
    "118": {"id": "idle-angry", "name": "Irritated", "duration": 26.07, "is_free": True},
    "119": {"id": "emote-baseball", "name": "Home Run!", "duration": 8.47, "is_free": True},
    "120": {"id": "emote-basketball", "name": "Basketball", "duration": 6.33, "is_free": True},
    "141": {"id": "idle-floorsleeping", "name": "Cozy Nap", "duration": 14.61, "is_free": True},
    "142": {"id": "idle-floorsleeping2", "name": "Relaxing", "duration": 18.83, "is_free": True},
    "143": {"id": "emote-hugyourself", "name": "Hug Yourself", "duration": 6.03, "is_free": True},
    "144": {"id": "idle-sad", "name": "Pouty Face", "duration": 25.24, "is_free": True},
    "145": {"id": "emote-death2", "name": "Collapse", "duration": 5.54, "is_free": True},
    "146": {"id": "emote-levelup", "name": "Level Up!", "duration": 7.27, "is_free": True},
    "147": {"id": "idle-posh", "name": "Posh", "duration": 23.29, "is_free": True},
    "148": {"id": "emote-snowangel", "name": "Snow Angel", "duration": 7.33, "is_free": True},
    "149": {"id": "emote-hot", "name": "Sweating", "duration": 5.57, "is_free": True},
    "150": {"id": "emote-snowball", "name": "Snowball Fight!", "duration": 6.32, "is_free": True},
    "151": {"id": "idle-lookup", "name": "Ponder", "duration": 8.75, "is_free": True},
    "152": {"id": "emote-curtsy", "name": "Curtsy", "duration": 3.99, "is_free": True},
    "153": {"id": "dance-russian", "name": "Russian Dance", "duration": 11.39, "is_free": True},
    "154": {"id": "emote-bow", "name": "Bow", "duration": 5.10, "is_free": True},
    "155": {"id": "emote-boo", "name": "Boo", "duration": 5.58, "is_free": True},
    "156": {"id": "emote-fail1", "name": "Fall", "duration": 6.90, "is_free": True},
    "157": {"id": "emote-fail2", "name": "Clumsy", "duration": 7.74, "is_free": True},
    "158": {"id": "emote-jetpack", "name": "Imaginary Jetpack", "duration": 17.77, "is_free": True},
    "159": {"id": "emote-death", "name": "Revival", "duration": 8.00, "is_free": True},
    "160": {"id": "dance-pennywise", "name": "Penny's Dance", "duration": 4.16, "is_free": True},
    "161": {"id": "idle-sleep", "name": "Sleepy", "duration": 3.35, "is_free": True},
    "162": {"id": "idle_layingdown", "name": "Attentive", "duration": 26.11, "is_free": True},
    "163": {"id": "emote-theatrical", "name": "Theatrical", "duration": 11.00, "is_free": True},
    "164": {"id": "emote-fainting", "name": "Faint", "duration": 18.55, "is_free": True},
    "165": {"id": "idle_layingdown2", "name": "Relaxed", "duration": 22.59, "is_free": True},
    "166": {"id": "emote-wings", "name": "I Believe I Can Fly", "duration": 14.21, "is_free": True},
    "167": {"id": "emote-laughing2", "name": "Amused", "duration": 6.60, "is_free": True},
    "168": {"id": "dance-tiktok2", "name": "Don't Start Now", "duration": 11.37, "is_free": True},
    "169": {"id": "emote-model", "name": "Model", "duration": 7.43, "is_free": True},
    "170": {"id": "dance-blackpink", "name": "K-Pop Dance", "duration": 7.97, "is_free": True},
    "171": {"id": "emoji-sick", "name": "Sick", "duration": 6.22, "is_free": True},
    "172": {"id": "idle_zombie", "name": "Zombie", "duration": 31.39, "is_free": True},
    "173": {"id": "emote-cold", "name": "Cold", "duration": 5.17, "is_free": True},
    "174": {"id": "emote-bunnyhop", "name": "Bunny Hop", "duration": 13.63, "is_free": True},
    "175": {"id": "emote-disco", "name": "Disco", "duration": 6.14, "is_free": True},
    "176": {"id": "dance-sexy", "name": "Wiggle Dance", "duration": 13.70, "is_free": True},
    "177": {"id": "emote-heartfingers", "name": "Heart Hands", "duration": 5.18, "is_free": True},
    "178": {"id": "dance-tiktok8", "name": "Savage Dance", "duration": 13.10, "is_free": True},
    "179": {"id": "emote-ghost-idle", "name": "Ghost Float", "duration": 20.43, "is_free": True},
    "180": {"id": "emoji-sneeze", "name": "Sneeze", "duration": 4.33, "is_free": True},
    "181": {"id": "emoji-pray", "name": "Pray", "duration": 6.00, "is_free": True},
    "182": {"id": "emote-handstand", "name": "Handstand", "duration": 5.89, "is_free": True},
    "183": {"id": "dance-smoothwalk", "name": "Smoothwalk", "duration": 7.58, "is_free": True},
    "184": {"id": "dance-singleladies", "name": "Ring on It", "duration": 22.33, "is_free": True},
    "185": {"id": "emote-heartshape", "name": "Partner Heart Arms", "duration": 7.60, "is_free": True},
    "186": {"id": "emoji-ghost", "name": "Ghost", "duration": 3.74, "is_free": True},
    "187": {"id": "dance-aerobics", "name": "Push Ups", "duration": 9.89, "is_free": True},
    "188": {"id": "emoji-naughty", "name": "Naughty", "duration": 5.73, "is_free": True},
    "189": {"id": "emote-deathdrop", "name": "Faint Drop", "duration": 4.18, "is_free": True},
    "190": {"id": "dance-duckwalk", "name": "Duck Walk", "duration": 12.48, "is_free": True},
    "191": {"id": "emote-splitsdrop", "name": "Splits Drop", "duration": 5.31, "is_free": True},
    "192": {"id": "dance-voguehands", "name": "Vogue Hands", "duration": 10.57, "is_free": True},
    "193": {"id": "emoji-give-up", "name": "Give Up", "duration": 6.04, "is_free": True},
    "194": {"id": "emoji-smirking", "name": "Smirk", "duration": 5.74, "is_free": True},
    "195": {"id": "emoji-lying", "name": "Lying", "duration": 7.39, "is_free": True},
    "196": {"id": "emoji-arrogance", "name": "Arrogance", "duration": 8.16, "is_free": True},
    "197": {"id": "emoji-there", "name": "Point", "duration": 3.09, "is_free": True},
    "198": {"id": "emoji-poop", "name": "Stinky", "duration": 5.86, "is_free": True},
    "199": {"id": "emoji-hadoken", "name": "Fireball Lunge", "duration": 4.29, "is_free": True},
    "200": {"id": "emoji-punch", "name": "Punch", "duration": 3.36, "is_free": True},
    "201": {"id": "dance-handsup", "name": "Hands in the Air", "duration": 23.18, "is_free": True},
    "202": {"id": "dance-metal", "name": "Rock Out", "duration": 15.78, "is_free": True},
    "203": {"id": "dance-orangejustice", "name": "Orange Juice Dance", "duration": 7.17, "is_free": True},
    "204": {"id": "idle-loop-aerobics", "name": "Aerobics", "duration": 10.08, "is_free": True},
    "205": {"id": "idle-loop-annoyed", "name": "Annoyed", "duration": 18.62, "is_free": True},
    "206": {"id": "emoji-scared", "name": "Gasp", "duration": 4.06, "is_free": True},
    "207": {"id": "emote-think", "name": "Think", "duration": 4.81, "is_free": True},
    "208": {"id": "idle-loop-tired", "name": "Fatigued", "duration": 11.23, "is_free": True},
    "209": {"id": "idle-dance-headbobbing", "name": "Feel The Beat", "duration": 23.65, "is_free": True},
    "210": {"id": "emote-disappear", "name": "Blast Off", "duration": 5.53, "is_free": True},
    "211": {"id": "emoji-crying", "name": "Sob", "duration": 4.91, "is_free": True},
    "212": {"id": "idle-loop-tapdance", "name": "Tap Loop", "duration": 7.81, "is_free": True},
    "213": {"id": "emoji-celebrate", "name": "Raise The Roof", "duration": 4.78, "is_free": True},
    "214": {"id": "emoji-eyeroll", "name": "Eye Roll", "duration": 3.75, "is_free": True},
    "215": {"id": "emoji-dizzy", "name": "Stunned", "duration": 5.38, "is_free": True},
    "216": {"id": "emoji-gagging", "name": "Tummy Ache", "duration": 6.84, "is_free": True},
    "217": {"id": "emote-greedy", "name": "Greedy Emote", "duration": 5.72, "is_free": True},
    "218": {"id": "emoji-mind-blown", "name": "Mind Blown", "duration": 3.46, "is_free": True},
    "219": {"id": "emote-shy", "name": "Shy", "duration": 5.15, "is_free": True},
    "220": {"id": "emoji-clapping", "name": "Clap", "duration": 2.98, "is_free": True},
    "221": {"id": "emote-hearteyes", "name": "Love Flutter", "duration": 5.99, "is_free": True},
    "222": {"id": "emote-suckthumb", "name": "Thumb Suck", "duration": 5.23, "is_free": True},
    "223": {"id": "emote-exasperated", "name": "Exasperated", "duration": 4.10, "is_free": True},
    "224": {"id": "emote-jumpb", "name": "Jump", "duration": 4.87, "is_free": True},
    "225": {"id": "emote-exasperatedb", "name": "Face Palm", "duration": 3.89, "is_free": True},
    "226": {"id": "emote-peace", "name": "Peace", "duration": 7.01, "is_free": True},
    "227": {"id": "emote-wave", "name": "The Wave", "duration": 4.06, "is_free": True},
    "228": {"id": "emote-panic", "name": "Panic", "duration": 3.72, "is_free": True}
}

def load_config():
    """Загружает конфигурацию из файла"""
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}

def save_data(filename: str, data: dict):
    """Сохраняет данные в файл"""
    try:
        os.makedirs("data", exist_ok=True)
        with open(f"data/{filename}", "w", encoding="utf-8") as f:
            if isinstance(data, dict):
                # Преобразуем datetime объекты в строки для сериализации
                serializable_data = {}
                for key, value in data.items():
                    if isinstance(value, dict):
                        serializable_data[key] = {}
                        for k, v in value.items():
                            if isinstance(v, datetime):
                                serializable_data[key][k] = v.isoformat()
                            else:
                                serializable_data[key][k] = v
                    elif isinstance(value, datetime):
                        serializable_data[key] = value.isoformat()
                    else:
                        serializable_data[key] = value
                json.dump(serializable_data, f, indent=2, ensure_ascii=False)
            else:
                json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving {filename}: {e}")

def load_data(filename: str) -> dict:
    """Загружает данные из файла"""
    try:
        with open(f"data/{filename}", "r", encoding="utf-8") as f:
            data = json.load(f)
            # Преобразуем строки обратно в datetime объекты
            if filename in ["marriages.json", "warnings.json", "vip_users.json"]:
                for user_id, user_data in data.items():
                    if isinstance(user_data, dict):
                        for key, value in user_data.items():
                            if key in ["date", "last_warning", "expires"] and isinstance(value, str):
                                try:
                                    data[user_id][key] = datetime.fromisoformat(value)
                                except:
                                    pass
            return data
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return {}

# Загружаем конфигурацию
config = load_config()
ADMIN_IDS = config.get("admin_ids", [])
OWNER_ID = config.get("owner_id", "")
MODERATOR_IDS = config.get("moderator_ids", [])
VIP_ZONE = config.get("vip_zone", {"x": 16, "y": 15, "z": 16})
DUEL_ARENA = config.get("duel_arena", {"x": 16, "y": 15, "z": 16})
DUEL_LOCATION = config.get("duel_location", {})
VIP_PRICE_MONTHLY = config.get("vip_price_monthly", 1)
MARRIAGE_DIVORCE_COST = config.get("marriage_divorce_cost", 50)
FREE_DIVORCE_DAYS = config.get("free_divorce_days", 14)
WARNING_EXPIRE_DAYS = config.get("warning_expire_days", 1)

# Загружаем данные при старте
MARRIAGES = load_data("marriages.json")
DIVORCE_COUNT = load_data("divorce_count.json")
WARNINGS = load_data("warnings.json")
VIP_USERS = load_data("vip_users.json")
USER_LEVELS = load_data("user_levels.json")
MESSAGE_COUNT = load_data("message_count.json")
CUSTOM_TP_POINTS = load_data("teleport_points.json")
VIP_SAVINGS = load_data("vip_savings.json")
USER_PROFILES = load_data("user_profiles.json")
BOT_SPAWN_POSITION = load_data("bot_spawn_position.json")
WISHES_SUGGESTIONS = load_data("wishes_suggestions.json")

# Глобальные переменные для анимаций
ACTIVE_ANIMATIONS = {}  # {user_id: {"emote_id": str, "task": asyncio.Task}}

class Bot(BaseBot):
    def __init__(self):
        super().__init__()
        self.bot_id = None
        self.owner_id = None
        self.last_announcement = datetime.now()
        
    async def on_start(self, session_metadata: SessionMetadata) -> None:
        try:
            # Сохраняем ID бота и владельца
            self.bot_id = session_metadata.user_id
            self.owner_id = session_metadata.room_info.owner_id
            
            print(f"Бот подключен к комнате: {session_metadata.room_info.room_id if hasattr(session_metadata.room_info, 'room_id') else 'Unknown'}")
            print("Бот успешно подключен!")
            
            # Обновляем список модераторов комнаты
            await self.update_room_moderators()
            
            # Запускаем задачи
            asyncio.create_task(self.start_announcements())
            asyncio.create_task(self.cleanup_expired_data())
            
            # Телепортируем бота на сохраненную позицию
            await self.teleport_bot_to_spawn_position()
        except Exception as e:
            print(f"Ошибка в on_start: {e}")
        
    async def cleanup_expired_data(self):
        """Очищает устаревшие данные"""
        while True:
            try:
                current_time = datetime.now()
                
                # Очищаем устаревшие предупреждения
                to_remove = []
                for user_id, warning_data in WARNINGS.items():
                    if (current_time - warning_data["last_warning"]).days >= WARNING_EXPIRE_DAYS:
                        if warning_data["count"] == 1:
                            to_remove.append(user_id)
                        else:
                            WARNINGS[user_id]["count"] = 1
                            WARNINGS[user_id]["last_warning"] = current_time
                
                for user_id in to_remove:
                    del WARNINGS[user_id]
                
                save_data("warnings.json", WARNINGS)
                
                # Очищаем устаревшие запросы на дуэль
                to_remove = []
                for user_id, duel_data in DUEL_REQUESTS.items():
                    if (current_time - duel_data["timestamp"]).seconds > 60:  # 1 минута
                        to_remove.append(user_id)
                
                for user_id in to_remove:
                    del DUEL_REQUESTS[user_id]
                
                # Очищаем устаревшие предложения брака
                to_remove = []
                for user_id, proposal_data in MARRIAGE_PROPOSALS.items():
                    if (current_time - proposal_data["timestamp"]).seconds > 60:  # 1 минута
                        to_remove.append(user_id)
                
                for user_id in to_remove:
                    del MARRIAGE_PROPOSALS[user_id]
                
                await asyncio.sleep(300)  # Проверяем каждые 5 минут
                
            except Exception as e:
                print(f"Error in cleanup: {e}")
                await asyncio.sleep(60)

    def is_admin(self, user_id: str) -> bool:
        """Проверяет, является ли пользователь администратором"""
        return user_id in ADMIN_IDS or user_id == OWNER_ID

    def is_moderator(self, user_id: str) -> bool:
        """Проверяет, является ли пользователь модератором"""
        global MODERATOR_IDS, VIP_USERS
        is_mod = user_id in MODERATOR_IDS or self.is_admin(user_id)
        
        # Автоматически даем VIP статус модераторам
        if is_mod and user_id not in VIP_USERS:
            VIP_USERS[user_id] = {
                "expires": datetime.now() + timedelta(days=365),  # VIP на год
                "tp_uses": 0,
                "prank_uses": 0
            }
            save_data("vip_users.json", VIP_USERS)
            print(f"Автоматически дан VIP статус модератору {user_id}")
        
        return is_mod

    def is_owner(self, user_id: str) -> bool:
        """Проверяет, является ли пользователь владельцем"""
        return user_id == OWNER_ID

    def has_full_access(self, user_id: str) -> bool:
        """Проверяет, есть ли у пользователя полный доступ (владелец или админ)"""
        return self.is_owner(user_id) or self.is_admin(user_id)

    def is_vip(self, user_id: str) -> bool:
        global VIP_USERS
        if self.is_moderator(user_id):
            return True
        
        if user_id in VIP_USERS:
            vip_data = VIP_USERS[user_id]
            if vip_data["expires"] > datetime.now():
                return True
            else:
                # VIP истек
                del VIP_USERS[user_id]
                save_data("vip_users.json", VIP_USERS)
        
        return False

    def get_user_level(self, user_id: str) -> int:
        """Получает уровень пользователя"""
        if user_id not in USER_LEVELS:
            USER_LEVELS[user_id] = {"level": 1, "messages": 0}
        return USER_LEVELS[user_id]["level"]

    def add_message_count(self, user_id: str, username: str):
        """Добавляет сообщение к счетчику и проверяет уровень"""
        if user_id not in MESSAGE_COUNT:
            MESSAGE_COUNT[user_id] = {"count": 0, "username": username}
        
        MESSAGE_COUNT[user_id]["count"] += 1
        MESSAGE_COUNT[user_id]["username"] = username
        
        if user_id not in USER_LEVELS:
            USER_LEVELS[user_id] = {"level": 1, "messages": 0}
        
        USER_LEVELS[user_id]["messages"] += 1
        
        # Проверяем повышение уровня
        current_level = USER_LEVELS[user_id]["level"]
        messages = USER_LEVELS[user_id]["messages"]
        
        # Формула для уровней: 100 * level для следующего уровня
        required_messages = 100 * current_level
        
        if messages >= required_messages:
            USER_LEVELS[user_id]["level"] += 1
            USER_LEVELS[user_id]["messages"] = 0
            save_data("user_levels.json", USER_LEVELS)
            return True  # Повышение уровня
        
        save_data("message_count.json", MESSAGE_COUNT)
        save_data("user_levels.json", USER_LEVELS)
        return False

    async def send_whisper(self, user_id: str, message: str):
        """Отправляет приватное сообщение пользователю"""
        try:
            # Разбиваем длинные сообщения на части
            if len(message) > 200:
                parts = [message[i:i+200] for i in range(0, len(message), 200)]
                for part in parts:
                    await self.highrise.send_whisper(user_id, part)
                    await asyncio.sleep(0.1)  # Небольшая пауза между частями
            else:
                await self.highrise.send_whisper(user_id, message)
        except Exception as e:
            print(f"Error sending whisper to {user_id}: {e}")

    async def teleport_user(self, user_id: str, x: float, y: float, z: float):
        """Телепортирует пользователя с повторными попытками"""
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                await self.highrise.teleport(user_id, Position(x, y, z))
                return True  # Успешная телепортация
            except Exception as e:
                print(f"Teleport attempt {attempt + 1}/{max_attempts} failed for user {user_id} to ({x}, {y}, {z}): {e}")
                if attempt < max_attempts - 1:
                    await asyncio.sleep(0.3)  # Пауза перед повторной попыткой
                else:
                    print(f"All teleport attempts failed for user {user_id}")
                    return False  # Все попытки неудачны

    async def send_emote(self, user_id: str, emote_id: str):
        """Отправляет эмоцию пользователю"""
        try:
            await self.highrise.send_emote(emote_id, user_id)
        except Exception as e:
            print(f"Error sending emote to {user_id}: {e}")

    async def send_emote_loop(self, user_id: str, emote_id: str):
        """Отправляет эмоцию в цикле"""
        global ACTIVE_ANIMATIONS
        try:
            while user_id in ACTIVE_ANIMATIONS and ACTIVE_ANIMATIONS[user_id]["emote_id"] == emote_id:
                # Проверяем, не была ли задача отменена
                if asyncio.current_task().cancelled():
                    print(f"Задача анимации отменена для {user_id}")
                    break
                
                await self.highrise.send_emote(emote_id, user_id)
                
                # Получаем длительность анимации
                duration = 20.0  # По умолчанию 20 секунд
                for key, data in emotes.items():
                    if data.get("id") == emote_id:
                        duration = data.get("duration", 20.0)
                        break
                
                # Ждем полную длительность анимации + 2 секунды паузы
                wait_time = duration + 2.0
                print(f"Анимация {emote_id} для {user_id}: длительность {duration:.1f}с, ожидание {wait_time:.1f}с")
                
                try:
                    await asyncio.sleep(wait_time)
                except asyncio.CancelledError:
                    print(f"Ожидание анимации отменено для {user_id}")
                    break
                
        except asyncio.CancelledError:
            print(f"Цикл анимации отменен для {user_id}")
        except Exception as e:
            print(f"Error in emote loop for {user_id}: {e}")
        finally:
            # Удаляем из активных анимаций если цикл завершен
            if user_id in ACTIVE_ANIMATIONS and ACTIVE_ANIMATIONS[user_id]["emote_id"] == emote_id:
                del ACTIVE_ANIMATIONS[user_id]
                print(f"Анимация удалена из активных для {user_id}")

    async def start_emote_loop(self, user_id: str, emote_id: str):
        """Запускает цикличную анимацию"""
        global ACTIVE_ANIMATIONS
        
        # Останавливаем предыдущую анимацию если есть
        await self.stop_emote_loop(user_id)
        
        # Создаем новую задачу для цикличной анимации
        task = asyncio.create_task(self.send_emote_loop(user_id, emote_id))
        ACTIVE_ANIMATIONS[user_id] = {
            "emote_id": emote_id,
            "task": task
        }
        print(f"Запущена цикличная анимация {emote_id} для пользователя {user_id}")

    async def stop_emote_loop(self, user_id: str):
        """Принудительно останавливает цикличную анимацию"""
        global ACTIVE_ANIMATIONS
        
        print(f"Попытка остановки анимации для пользователя {user_id}")
        
        if user_id in ACTIVE_ANIMATIONS:
            try:
                # Отменяем задачу
                task = ACTIVE_ANIMATIONS[user_id]["task"]
                task.cancel()
                
                # Ждем отмены задачи
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                
                # Удаляем из активных анимаций
                del ACTIVE_ANIMATIONS[user_id]
                print(f"Задача анимации отменена для пользователя {user_id}")
                
            except Exception as e:
                print(f"Ошибка при отмене задачи: {e}")
                # Принудительно удаляем из активных анимаций
                if user_id in ACTIVE_ANIMATIONS:
                    del ACTIVE_ANIMATIONS[user_id]
        
        # Принудительная остановка - отправляем базовую анимацию
        try:
            # Пробуем разные базовые анимации, которые доступны всем
            basic_emotes = ["emote-wave", "emote-hello", "emote-smile", "emote-dance", "emote-clap"]
            
            emote_sent = False
            for emote in basic_emotes:
                try:
                    await self.highrise.send_emote(emote, user_id)
                    print(f"Принудительная остановка выполнена для пользователя {user_id} с анимацией {emote}")
                    emote_sent = True
                    break  # Если одна анимация сработала, останавливаемся
                except Exception as emote_error:
                    print(f"Анимация {emote} недоступна для {user_id}: {emote_error}")
                    continue
            
            if not emote_sent:
                print(f"Все базовые анимации недоступны для {user_id}, но задача анимации отменена")
            
        except Exception as e:
            print(f"Ошибка при принудительной остановке: {e}")



    async def kick_user(self, user_id: str):
        """Кикает пользователя"""
        try:
            await self.highrise.moderate_room(user_id, "kick", None)
        except Exception as e:
            print(f"Error kicking user {user_id}: {e}")

    async def ban_user(self, user_id: str):
        """Банит пользователя"""
        try:
            await self.highrise.moderate_room(user_id, "ban", None)
        except Exception as e:
            print(f"Error banning user {user_id}: {e}")

    async def on_user_join(self, user: User, position: Position) -> None:
        """Обработка входа пользователя"""
        username = user.username
        user_id = user.id
        
        # Получаем и сохраняем профиль пользователя
        await self.update_user_profile(user)
        
        # Проверяем VIP статус для приветствия
        if self.is_vip(user_id):
            await self.highrise.chat(f"Вип игрок @{username} зашел в комнату! Местная звезда теперь с нами! ⭐")
        else:
            await self.highrise.chat(f"Добро пожаловать в комнату @{username}, чувствуй себя как дома 🎀")

    async def update_user_profile(self, user: User):
        """Обновляет профиль пользователя через API"""
        try:
            # Получаем данные пользователя через API
            response = await self.webapi.get_user(user.id)
            user_data = response.user
            
            # Сохраняем профиль
            USER_PROFILES[user.id] = {
                "username": user_data.username,
                "bio": user_data.bio,
                "joined_at": str(user_data.joined_at),
                "num_followers": user_data.num_followers,
                "num_following": user_data.num_following,
                "num_friends": user_data.num_friends,
                "country_code": user_data.country_code,
                "crew": user_data.crew.name if user_data.crew else "Нет команды",
                "last_seen": str(user_data.last_online_in) if user_data.last_online_in else "Неизвестно",
                "last_updated": str(datetime.now())
            }
            
            # Сохраняем в файл
            save_data("user_profiles.json", USER_PROFILES)
            
            print(f"Профиль пользователя {user.username} обновлен")
            
        except Exception as e:
            print(f"Ошибка при обновлении профиля пользователя {user.username}: {e}")
            # Сохраняем базовую информацию если API недоступен
            USER_PROFILES[user.id] = {
                "username": user.username,
                "bio": "Недоступно",
                "joined_at": "Неизвестно",
                "num_followers": 0,
                "num_following": 0,
                "num_friends": 0,
                "country_code": "",
                "crew": "Неизвестно",
                "last_seen": str(datetime.now()),
                "last_updated": str(datetime.now())
            }
            save_data("data/user_profiles.json", USER_PROFILES)
    
    async def update_room_moderators(self):
        """Обновляет список модераторов комнаты"""
        global MODERATOR_IDS
        try:
            # Пока что просто используем модераторов из конфигурации
            # API для получения модераторов комнаты может быть недоступен
            print(f"Список модераторов из конфигурации: {MODERATOR_IDS}")
            
        except Exception as e:
            print(f"Ошибка при обновлении модераторов: {e}")

    async def start_announcements(self):
        """Запускает автоматические объявления"""
        while True:
            try:
                await asyncio.sleep(config.get("announcement_interval", 600))  # 10 минут
                announcements = config.get("announcements", [])
                if announcements:
                    message = random.choice(announcements)
                    await self.highrise.chat(message)
            except Exception as e:
                print(f"Error in announcements: {e}")
                await asyncio.sleep(60)

    async def on_chat(self, user: User, message: str) -> None:
        """Обработка сообщений в чате"""
        username = user.username
        user_id = user.id
        message = message.strip()
        
        # Добавляем к счетчику сообщений
        level_up = self.add_message_count(user_id, username)
        if level_up:
            current_level = self.get_user_level(user_id)
            await self.highrise.chat(f"🎉 Поздравляем @{username}! Вы достигли {current_level} уровня!")

        # Обработка команд
        if message.startswith("дуэль @"):
            await self.handle_duel_request(user, message)
        elif message.startswith("брак @"):
            await self.handle_marriage_proposal(user, message)
        elif message.startswith("развод @"):
            await self.handle_divorce_request(user, message)
        elif message.lower() == "мой брак":
            await self.show_marriage_status(user)
        elif message.lower() == "мои разводы":
            await self.show_divorce_count(user)
        elif message.lower() == "вип":
            await self.handle_vip_request(user)
        elif message.startswith("вип тп @") and (self.is_vip(user_id) or self.is_moderator(user_id) or self.has_full_access(user_id)):
            await self.handle_vip_tp_to_self(user, message)
        elif message.lower() == "вип тп" and (self.is_vip(user_id) or self.is_moderator(user_id) or self.has_full_access(user_id)):
            await self.handle_vip_tp_to_self(user, "вип тп")
        elif message.startswith("тп @") and (self.is_vip(user_id) or self.is_moderator(user_id) or self.has_full_access(user_id)):
            await self.handle_tp_player_to_self(user, message)
        elif message.startswith("к @"):
            await self.handle_tp_to_player(user, message)
        elif message.startswith("тпк "):
            await self.handle_tp_coords(user, message)
        elif message.lower() == "тп к себе" and (self.is_vip(user_id) or self.is_moderator(user_id) or self.has_full_access(user_id)):
            await self.handle_tp_to_self_limited(user)
        elif message.startswith("пранк @") and self.is_vip(user_id):
            await self.handle_vip_prank(user, message)

        elif message.startswith("пред @") and self.has_full_access(user_id):
            await self.handle_warning(user, message)
        elif message.startswith("кик @") and self.has_full_access(user_id):
            await self.handle_kick(user, message)
        elif message.startswith("бан @") and self.has_full_access(user_id):
            await self.handle_ban(user, message)
        elif message.startswith("!emote "):
            await self.handle_emote_command(user, message)
        elif message.lower() == "топ сообщения":
            await self.show_message_leaderboard(user)
        elif message.lower() == "мой уровень":
            await self.show_user_level(user)
        elif message.startswith("!TPus "):
            await self.handle_create_tp_point(user, message)
        elif message.lower() in ["топ сообщения", "!топ", "топ"]:
            await self.show_message_leaderboard(user)
        elif message.lower() in ["мой уровень", "!уровень", "уровень"]:
            await self.show_user_level(user)
        elif message == "!rights" and self.has_full_access(user_id):
            await self.show_user_rights(user)
        elif message.startswith("!addadmin ") and self.is_owner(user_id):
            await self.add_admin(user, message)
        elif message.startswith("!removeadmin ") and self.is_owner(user_id):
            await self.remove_admin(user, message)
        elif message.startswith("!removevip ") and self.is_owner(user_id):
            await self.remove_vip(user, message)
        elif message.startswith("!resetvip ") and self.is_owner(user_id):
            await self.reset_vip_limits(user, message)
        elif message.startswith("!setvipzone") and self.is_owner(user_id):
            await self.set_vip_zone(user)
        elif message.startswith("!addmod ") and self.is_owner(user_id):
            await self.add_moderator(user, message)
        elif message.startswith("!setduel") and self.is_owner(user_id):
            await self.set_duel_location(user)
        elif message.lower() == "!info":
            await self.show_user_info(user)
        elif message.lower() == "!bot tp" and self.is_owner(user_id):
            await self.teleport_bot_to_owner(user)
        elif message.lower() == "!setspawn" and self.is_owner(user_id):
            await self.set_bot_spawn_position(user)
        elif message.startswith("!flirt @") and len(message.split()) == 2:
            await self.handle_flirt_command(user, message)
        elif message.startswith("!wish "):
            await self.handle_wish_command(user, message)
        elif message.lower() in ["да", "нет"]:
            await self.handle_duel_response(user, message)
        elif message.lower() in ["согласиться", "отказаться"]:
            await self.handle_marriage_response(user, message)
        elif message.lower() in ["0", "стоп"]:
            await self.stop_emote_loop(user_id)
            await self.send_whisper(user_id, "Анимация остановлена!")
        elif message.lower() == "!стоп":
            await self.stop_emote_loop(user_id)
            await self.send_whisper(user_id, "Принудительная остановка анимации выполнена!")
        elif message.lower() == "стоп без анимации":
            # Останавливаем только задачу без отправки новой анимации
            global ACTIVE_ANIMATIONS
            if user_id in ACTIVE_ANIMATIONS:
                try:
                    task = ACTIVE_ANIMATIONS[user_id]["task"]
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
                    del ACTIVE_ANIMATIONS[user_id]
                    await self.send_whisper(user_id, "Анимация остановлена без отправки новой анимации!")
                except Exception as e:
                    print(f"Ошибка при остановке без анимации: {e}")
                    await self.send_whisper(user_id, "Ошибка при остановке анимации!")
            else:
                await self.send_whisper(user_id, "У вас нет активной анимации!")
        elif message.lower() in ["гост", "ghost", "ghostfloat"]:
            await self.start_emote_loop(user_id, "emote-ghost-idle")
            await self.send_whisper(user_id, "Цикличная анимация 'Ghost Float' запущена! Напишите '0' или 'стоп' для остановки.")
        elif len(message.split()) == 2 and message.split()[0].isdigit() and "@" in message:
            # Анимация по ID другому игроку: "ID @username"
            await self.handle_emote_to_player_by_id(user, message)
        elif message.startswith("название @") and len(message.split()) >= 3:
            # Анимация по названию другому игроку
            await self.handle_emote_to_player_by_name(user, message)
        else:
            # Проверяем точки телепортации
            await self.handle_teleport_point(user, message)
            # Проверяем анимации по названию/ID (только для коротких сообщений и цифр)
            if (len(message) <= 20 and message.isdigit()) or (len(message) <= 15 and not message.startswith("!") and not message.startswith("@") and not message.startswith("дуэль") and not message.startswith("брак") and not message.startswith("развод") and not message.startswith("пред") and not message.startswith("кик") and not message.startswith("бан") and not message.startswith("вип") and not message.startswith("пранк") and not message.startswith("тп") and not message.startswith("мой") and not message.startswith("топ") and not message.startswith("уровень") and not message.startswith("да") and not message.startswith("нет") and not message.startswith("согласиться") and not message.startswith("отказаться")):
                await self.handle_emote_by_name(user, message)

    async def handle_duel_request(self, user: User, message: str):
        """Обработка запроса на дуэль"""
        try:
            target_username = message.replace("дуэль @", "").strip()
            
            # Ищем пользователя в комнате
            room_users = await self.highrise.get_room_users()
            target_user = None
            for u, _ in room_users.content:
                if u.username.lower() == target_username.lower():
                    target_user = u
                    break
            
            if not target_user:
                await self.send_whisper(user.id, f"Пользователь @{target_username} не найден в комнате.")
                return
            
            if target_user.id == user.id:
                await self.send_whisper(user.id, "Нельзя вызвать на дуэль самого себя!")
                return
            
            # Сохраняем запрос на дуэль
            DUEL_REQUESTS[target_user.id] = {
                "opponent": user.id,
                "opponent_username": user.username,
                "timestamp": datetime.now()
            }
            
            await self.highrise.chat(f"@{target_user.username}, вас приглашают на дуэль! 🤺 Напишите в чат да/нет, чтобы ответить на запрос")
            
        except Exception as e:
            print(f"Error in duel request: {e}")

    async def handle_duel_response(self, user: User, message: str):
        """Обработка ответа на дуэль"""
        try:
            if user.id not in DUEL_REQUESTS:
                return
            
            duel_data = DUEL_REQUESTS[user.id]
            opponent_id = duel_data["opponent"]
            opponent_username = duel_data["opponent_username"]
            
            del DUEL_REQUESTS[user.id]
            
            if message.lower() == "да":
                await self.start_duel(user.id, user.username, opponent_id, opponent_username)
            else:
                await self.send_whisper(opponent_id, f"Увы, игрок отказался от участия в дуэле :(")
                
        except Exception as e:
            print(f"Error in duel response: {e}")

    async def start_duel(self, user1_id: str, user1_name: str, user2_id: str, user2_name: str):
        """Запускает дуэль между двумя игроками"""
        try:
            # Проверяем, установлено ли место дуэли
            if not DUEL_LOCATION:
                await self.highrise.chat("Место дуэли не установлено! Владелец должен использовать команду !setduel")
                return
            
            # Телепортируем игроков на арену
            duel_pos = DUEL_LOCATION
            await self.teleport_user(user1_id, duel_pos["x"], duel_pos["y"], duel_pos["z"])
            await self.teleport_user(user2_id, duel_pos["x"] + 2, duel_pos["y"], duel_pos["z"])
            
            await self.highrise.chat(f"🤺 Дуэль между @{user1_name} и @{user2_name} начинается!")
            
            # Ждем немного
            await asyncio.sleep(2)
            
            # Отправляем боевые анимации
            fight_emote1 = random.choice(FIGHT_EMOTES)
            fight_emote2 = random.choice(FIGHT_EMOTES)
            
            await self.send_emote(user1_id, fight_emote1)
            await self.send_emote(user2_id, fight_emote2)
            
            # Ждем анимации
            await asyncio.sleep(5)
            
            # Определяем результат
            result = random.choice(["user1_wins", "user2_wins", "draw"])
            
            if result == "user1_wins":
                await self.highrise.chat(f"🏆 @{user1_name} одержал/а победу над @{user2_name}. Желаю удачи в следующем раунде! ✊🏻")
            elif result == "user2_wins":
                await self.highrise.chat(f"🏆 @{user2_name} одержал/а победу над @{user1_name}. Желаю удачи в следующем раунде! ✊🏻")
            else:
                await self.highrise.chat(f"Бой завершился ничьей между @{user1_name} и @{user2_name}. Удачи в следующем раунде! ✊🏻")
                
        except Exception as e:
            print(f"Error in duel: {e}")

    async def handle_marriage_proposal(self, user: User, message: str):
        """Обработка предложения брака"""
        try:
            target_username = message.replace("брак @", "").strip()
            
            # Проверяем, не состоит ли пользователь уже в браке
            if user.id in MARRIAGES:
                partner_id = MARRIAGES[user.id]["partner"]
                # Ищем имя партнера
                partner_name = "Unknown"
                for uid, data in MESSAGE_COUNT.items():
                    if uid == partner_id:
                        partner_name = data["username"]
                        break
                await self.send_whisper(user.id, f"Вы уже состоите в браке с @{partner_name}!")
                return
            
            # Ищем пользователя в комнате
            room_users = await self.highrise.get_room_users()
            target_user = None
            for u, _ in room_users.content:
                if u.username.lower() == target_username.lower():
                    target_user = u
                    break
            
            if not target_user:
                await self.send_whisper(user.id, f"Пользователь @{target_username} не найден в комнате.")
                return
            
            if target_user.id == user.id:
                await self.send_whisper(user.id, "Нельзя жениться на самом себе!")
                return
            
            # Проверяем, не состоит ли цель уже в браке
            if target_user.id in MARRIAGES:
                await self.send_whisper(user.id, f"@{target_username} уже состоит в браке!")
                return
            
            # Сохраняем предложение брака
            MARRIAGE_PROPOSALS[target_user.id] = {
                "proposer": user.id,
                "proposer_username": user.username,
                "timestamp": datetime.now()
            }
            
            await self.highrise.chat(f"@{target_user.username}, вам сделали предложение вступить в брак! 💍 Напишите согласиться/отказаться, чтобы ответить")
            
        except Exception as e:
            print(f"Error in marriage proposal: {e}")

    async def handle_marriage_response(self, user: User, message: str):
        """Обработка ответа на предложение брака"""
        try:
            if user.id not in MARRIAGE_PROPOSALS:
                return
            
            proposal_data = MARRIAGE_PROPOSALS[user.id]
            proposer_id = proposal_data["proposer"]
            proposer_username = proposal_data["proposer_username"]
            
            del MARRIAGE_PROPOSALS[user.id]
            
            if message.lower() == "согласиться":
                # Создаем брак
                marriage_date = datetime.now()
                MARRIAGES[user.id] = {"partner": proposer_id, "date": marriage_date}
                MARRIAGES[proposer_id] = {"partner": user.id, "date": marriage_date}
                
                save_data("marriages.json", MARRIAGES)
                
                await self.highrise.chat(f"@{proposer_username} и @{user.username} вступили в брак! Счастья вам! 🥳")
            else:
                await self.highrise.chat("К сожалению брак не состоится :(")
                
        except Exception as e:
            print(f"Error in marriage response: {e}")

    async def handle_divorce_request(self, user: User, message: str):
        """Обработка запроса на развод"""
        try:
            target_username = message.replace("развод @", "").strip()
            
            # Проверяем, состоит ли пользователь в браке
            if user.id not in MARRIAGES:
                await self.send_whisper(user.id, "Вы не состоите в браке!")
                return
            
            partner_id = MARRIAGES[user.id]["partner"]
            
            # Проверяем, что партнер существует в браке
            if partner_id not in MARRIAGES:
                await self.send_whisper(user.id, "Ошибка: данные о браке повреждены. Обратитесь к администратору.")
                return
            
            # Проверяем имя партнера
            partner_name = "Unknown"
            for uid, data in MESSAGE_COUNT.items():
                if uid == partner_id:
                    partner_name = data["username"]
                    break
            
            if partner_name.lower() != target_username.lower():
                await self.send_whisper(user.id, f"Вы состоите в браке с @{partner_name}, а не с @{target_username}!")
                return
            
            # Проверяем количество разводов пользователя
            divorce_count = DIVORCE_COUNT.get(user.id, {}).get("count", 0)
            
            if divorce_count == 0:
                # Первый развод бесплатный
                cost = 0
                await self.send_whisper(user.id, "Первый развод бесплатный! Брак будет расторгнут.")
                
                # Увеличиваем счетчик разводов
                if user.id not in DIVORCE_COUNT:
                    DIVORCE_COUNT[user.id] = {"count": 0}
                DIVORCE_COUNT[user_id]["count"] += 1
                
                # Проводим развод
                try:
                    del MARRIAGES[user.id]
                    del MARRIAGES[partner_id]
                    save_data("marriages.json", MARRIAGES)
                    save_data("divorce_count.json", DIVORCE_COUNT)
                    
                    await self.highrise.chat(f"Брак между @{user.username} и @{partner_name} был расторгнут 💔")
                except Exception as e:
                    print(f"Error during divorce execution: {e}")
                    await self.send_whisper(user.id, "Произошла ошибка при разводе. Попробуйте еще раз.")
            else:
                # Последующие разводы стоят 50 золота
                cost = MARRIAGE_DIVORCE_COST
                await self.send_whisper(user.id, f"Это ваш {divorce_count + 1}-й развод. Стоимость: {cost} золота. Отправьте боту чаевые для развода.")
                return
            
        except Exception as e:
            print(f"Error in divorce: {e}")

    async def show_marriage_status(self, user: User):
        """Показывает статус брака пользователя"""
        try:
            if user.id not in MARRIAGES:
                await self.send_whisper(user.id, "Вы не состоите в браке.")
                return
            
            marriage_data = MARRIAGES[user.id]
            partner_id = marriage_data["partner"]
            marriage_date = marriage_data["date"]
            
            # Ищем имя партнера
            partner_name = "Unknown"
            for uid, data in MESSAGE_COUNT.items():
                if uid == partner_id:
                    partner_name = data["username"]
                    break
            
            # Вычисляем время брака
            if isinstance(marriage_date, str):
                marriage_date = datetime.fromisoformat(marriage_date.replace('Z', '+00:00'))
            
            current_time = datetime.now()
            marriage_duration = current_time - marriage_date
            
            # Вычисляем дни, часы, минуты, секунды
            days = marriage_duration.days
            hours = marriage_duration.seconds // 3600
            minutes = (marriage_duration.seconds % 3600) // 60
            seconds = marriage_duration.seconds % 60
            
            # Формируем сообщение о времени брака
            time_parts = []
            if days > 0:
                time_parts.append(f"{days} дн")
            if hours > 0:
                time_parts.append(f"{hours} ч")
            if minutes > 0:
                time_parts.append(f"{minutes} мин")
            if seconds > 0 or not time_parts:
                time_parts.append(f"{seconds} сек")
            
            marriage_time = " ".join(time_parts)
            
            # Формируем полное сообщение
            message = f"💕 Вы состоите в браке с @{partner_name}\n"
            message += f"📅 Дата свадьбы: {marriage_date.strftime('%d.%m.%Y %H:%M:%S')}\n"
            message += f"⏰ Время брака: {marriage_time}"
            
            await self.send_whisper(user.id, message)
            
        except Exception as e:
            print(f"Error showing marriage status: {e}")
            await self.send_whisper(user.id, "Ошибка при получении информации о браке.")

    async def show_divorce_count(self, user: User):
        """Показывает количество разводов пользователя"""
        try:
            divorce_count = DIVORCE_COUNT.get(user.id, {}).get("count", 0)
            
            if divorce_count == 0:
                await self.send_whisper(user.id, "У вас еще не было разводов. Первый развод будет бесплатным!")
            else:
                next_cost = MARRIAGE_DIVORCE_COST if divorce_count > 0 else 0
                await self.send_whisper(user.id, f"У вас было {divorce_count} разводов. Следующий развод будет стоить {next_cost} золота.")
                
        except Exception as e:
            print(f"Error showing divorce count: {e}")

    async def handle_vip_request(self, user: User):
        """Обработка запроса на VIP"""
        try:
            user_id = user.id
            
            if self.is_moderator(user_id):
                await self.send_whisper(user_id, "У вас уже есть VIP статус как у модератора!")
                return
            
            if self.is_vip(user_id):
                vip_data = VIP_USERS[user_id]
                expires = vip_data["expires"]
                
                # Вычисляем точное время до истечения VIP
                if isinstance(expires, str):
                    expires = datetime.fromisoformat(expires.replace('Z', '+00:00'))
                
                current_time = datetime.now()
                time_left = expires - current_time
                
                if time_left.total_seconds() <= 0:
                    # VIP истек
                    await self.send_whisper(user_id, "Ваш VIP статус истек! Отправьте чаевые для продления.")
                    return
                
                # Вычисляем дни, часы, минуты, секунды
                days = time_left.days
                hours = time_left.seconds // 3600
                minutes = (time_left.seconds % 3600) // 60
                seconds = time_left.seconds % 60
                
                # Формируем сообщение о времени
                time_parts = []
                if days > 0:
                    time_parts.append(f"{days} дн")
                if hours > 0:
                    time_parts.append(f"{hours} ч")
                if minutes > 0:
                    time_parts.append(f"{minutes} мин")
                if seconds > 0 or not time_parts:
                    time_parts.append(f"{seconds} сек")
                
                time_left_str = " ".join(time_parts)
                
                await self.send_whisper(user_id, f"⭐ У вас уже есть VIP статус!\n⏰ Осталось времени: {time_left_str}")
                return
            
            # Показываем текущие накопления
            current_savings = VIP_SAVINGS.get(user_id, {}).get("amount", 0)
            if current_savings > 0:
                needed = VIP_PRICE_MONTHLY - current_savings
                await self.send_whisper(user_id, f"VIP статус стоит {VIP_PRICE_MONTHLY}г в месяц. У вас накоплено: {current_savings}г. Осталось: {needed}г")
            else:
                await self.send_whisper(user_id, f"VIP статус стоит {VIP_PRICE_MONTHLY}г в месяц. Отправьте боту чаевые для покупки VIP.")
            
        except Exception as e:
            print(f"Error in VIP request: {e}")

    async def handle_vip_tp_to_self(self, user: User, message: str):
        """Обработка VIP телепорта в VIP зону"""
        try:
            # Проверяем права доступа: VIP, модераторы, администраторы, владелец
            if not (self.is_vip(user.id) or self.is_moderator(user.id) or self.has_full_access(user.id)):
                await self.send_whisper(user.id, "Эта команда доступна только VIP пользователям, модераторам и администраторам!")
                return
            
            # Проверяем, установлена ли VIP зона
            if not VIP_ZONE:
                await self.send_whisper(user.id, "VIP зона не установлена! Обратитесь к владельцу.")
                return
            
            # Если команда "вип тп" - телепортируем самого пользователя
            if message.lower() == "вип тп":
                # Проверяем лимит использований только для VIP (не для модераторов/админов)
                if self.is_vip(user.id) and not self.is_moderator(user.id) and not self.has_full_access(user.id):
                    if user.id in VIP_USERS:
                        if VIP_USERS[user.id]["tp_uses"] >= 10:
                            await self.send_whisper(user.id, "Вы исчерпали лимит телепортов на сегодня (10/10)!")
                            return
                
                # Телепортируем пользователя в VIP зону
                await self.teleport_user(user.id, VIP_ZONE["x"], VIP_ZONE["y"], VIP_ZONE["z"])
                
                # Увеличиваем счетчик использований только для VIP (не для модераторов)
                if self.is_vip(user.id) and not self.is_moderator(user.id) and not self.has_full_access(user.id):
                    if user.id not in VIP_USERS:
                        VIP_USERS[user.id] = {"expires": datetime.now() + timedelta(days=30), "tp_uses": 0, "prank_uses": 0}
                    
                    VIP_USERS[user.id]["tp_uses"] += 1
                    save_data("vip_users.json", VIP_USERS)
                    
                    uses_left = 10 - VIP_USERS[user.id]["tp_uses"]
                    await self.send_whisper(user.id, f"Вы телепортированы в VIP зону! Осталось использований: {uses_left}/10")
                else:
                    await self.send_whisper(user.id, "Вы телепортированы в VIP зону!")
            
            # Если команда "вип тп @username" - телепортируем указанного пользователя
            elif message.startswith("вип тп @"):
                target_username = message.replace("вип тп @", "").strip()
                
                # Ищем пользователя
                room_users = await self.highrise.get_room_users()
                target_user = None
                
                for u, _ in room_users.content:
                    if u.username.lower() == target_username.lower():
                        target_user = u
                        break
                
                if not target_user:
                    await self.send_whisper(user.id, f"Пользователь @{target_username} не найден в комнате.")
                    return
                
                # Проверяем, есть ли у цели VIP статус
                if not self.is_vip(target_user.id):
                    await self.send_whisper(user.id, f"Нельзя телепортировать @{target_username} в VIP зону - у него нет VIP статуса!")
                    return
                
                # Проверяем лимит использований только для VIP (не для модераторов/админов)
                if self.is_vip(user.id) and not self.has_full_access(user.id):
                    if user.id in VIP_USERS:
                        if VIP_USERS[user.id]["tp_uses"] >= 10:
                            await self.send_whisper(user.id, "Вы исчерпали лимит телепортов на сегодня (10/10)!")
                            return
                
                # Телепортируем цель в VIP зону
                await self.teleport_user(target_user.id, VIP_ZONE["x"], VIP_ZONE["y"], VIP_ZONE["z"])
                
                # Увеличиваем счетчик использований только для VIP
                if self.is_vip(user.id) and not self.has_full_access(user.id):
                    if user.id not in VIP_USERS:
                        VIP_USERS[user.id] = {"expires": datetime.now() + timedelta(days=30), "tp_uses": 0, "prank_uses": 0}
                    
                    VIP_USERS[user.id]["tp_uses"] += 1
                    save_data("vip_users.json", VIP_USERS)
                    
                    uses_left = 10 - VIP_USERS[user.id]["tp_uses"]
                    await self.send_whisper(user.id, f"@{target_username} телепортирован в VIP зону! Осталось использований: {uses_left}/10")
                else:
                    await self.send_whisper(user.id, f"@{target_username} телепортирован в VIP зону!")
            
        except Exception as e:
            print(f"Error in VIP teleport: {e}")
            await self.send_whisper(user.id, "Ошибка при телепортации в VIP зону.")

    async def handle_vip_prank(self, user: User, message: str):
        """Обработка VIP пранка"""
        try:
            if not self.is_vip(user.id):
                await self.send_whisper(user.id, "Эта команда доступна только VIP пользователям!")
                return
            
            # Проверяем лимит использований только для VIP (не для модераторов)
            if self.is_vip(user.id) and not self.is_moderator(user.id) and not self.has_full_access(user.id):
                if user.id in VIP_USERS:
                    if VIP_USERS[user.id]["prank_uses"] >= 3:
                        await self.send_whisper(user.id, "Вы исчерпали лимит пранков на сегодня (3/3)!")
                        return
            
            target_username = message.replace("пранк @", "").strip()
            
            # Ищем пользователя
            room_users = await self.highrise.get_room_users()
            target_user = None
            
            for u, _ in room_users.content:
                if u.username.lower() == target_username.lower():
                    target_user = u
                    break
            
            if not target_user:
                await self.send_whisper(user.id, f"Пользователь @{target_username} не найден в комнате.")
                return
            
            # Генерируем 100 случайных координат в пределах здания (комнаты)
            # Обычно комната 30x30, добавляем небольшой выход за границы (-2 до 32)
            random_coords = []
            for _ in range(100):
                x = random.randint(-2, 32)  # Немного выходит за границы комнаты
                y = random.randint(0, 10)   # Высота от 0 до 10 (ограничение)
                z = random.randint(-2, 32)  # Немного выходит за границы комнаты
                random_coords.append((x, y, z))
            
            # Перемешиваем координаты для случайности
            random.shuffle(random_coords)
            
            # Берем первые 10 координат для пранка (уменьшаем для надежности)
            prank_count = 10
            prank_coords = random_coords[:prank_count]
            
            # Увеличиваем счетчик использований только для VIP (не для модераторов)
            if self.is_vip(user.id) and not self.is_moderator(user.id) and not self.has_full_access(user.id):
                if user.id not in VIP_USERS:
                    VIP_USERS[user.id] = {"expires": datetime.now() + timedelta(days=30), "tp_uses": 0, "prank_uses": 0}
                
                VIP_USERS[user.id]["prank_uses"] += 1
                save_data("vip_users.json", VIP_USERS)
            
            # Телепортируем игрока в несколько мест подряд
            successful_teleports = 0
            for i, coord in enumerate(prank_coords):
                # Увеличиваем паузу перед каждой телепортацией
                await asyncio.sleep(1.0)  # Увеличиваем до 1 секунды
                
                # Пытаемся телепортировать с повторными попытками
                if await self.teleport_user(target_user.id, coord[0], coord[1], coord[2]):
                    successful_teleports += 1
                    print(f"Successful teleport {successful_teleports}/{prank_count} to {coord}")
                    
                    # Пауза после успешной телепортации
                    await asyncio.sleep(1.0)  # Увеличиваем до 1 секунды
                else:
                    print(f"Failed to teleport to coord {coord}")
                    # Небольшая пауза даже при ошибке
                    await asyncio.sleep(0.5)
            
            # Проверяем, было ли достаточно успешных телепортаций
            if self.is_vip(user.id) and not self.is_moderator(user.id) and not self.has_full_access(user.id):
                uses_left = 3 - VIP_USERS[user.id]["prank_uses"]
                if successful_teleports >= 5:
                    await self.send_whisper(user.id, f"Пранк выполнен! @{target_username} был телепортирован в {successful_teleports} случайных мест! Осталось использований: {uses_left}/3")
                else:
                    await self.send_whisper(user.id, f"Пранк выполнен частично! @{target_username} был телепортирован в {successful_teleports} мест из {prank_count} запланированных. Осталось использований: {uses_left}/3")
            else:
                # Для модераторов - бесконечные пранки
                if successful_teleports >= 5:
                    await self.send_whisper(user.id, f"Пранк выполнен! @{target_username} был телепортирован в {successful_teleports} случайных мест! (Бесконечные пранки)")
                else:
                    await self.send_whisper(user.id, f"Пранк выполнен частично! @{target_username} был телепортирован в {successful_teleports} мест из {prank_count} запланированных. (Бесконечные пранки)")
            
        except Exception as e:
            print(f"Error in VIP prank: {e}")
            await self.send_whisper(user.id, "Ошибка при выполнении пранка.")

    async def handle_warning(self, user: User, message: str):
        """Обработка выдачи предупреждения"""
        try:
            # Проверяем права доступа
            if not self.has_full_access(user.id):
                await self.send_whisper(user.id, "Эта команда доступна только владельцу и администраторам!")
                return
            
            target_username = message.replace("пред @", "").strip()
            
            # Ищем пользователя
            room_users = await self.highrise.get_room_users()
            target_user = None
            
            for u, _ in room_users.content:
                if u.username.lower() == target_username.lower():
                    target_user = u
                    break
            
            if not target_user:
                await self.send_whisper(user.id, f"Пользователь @{target_username} не найден в комнате.")
                return
            
            if self.is_moderator(target_user.id):
                await self.send_whisper(user.id, "Нельзя выдать предупреждение модератору!")
                return
            
            # Добавляем предупреждение
            if target_user.id not in WARNINGS:
                WARNINGS[target_user.id] = {"count": 0, "last_warning": datetime.now()}
            
            WARNINGS[target_user.id]["count"] += 1
            WARNINGS[target_user.id]["last_warning"] = datetime.now()
            
            warning_count = WARNINGS[target_user.id]["count"]
            
            if warning_count == 1:
                await self.highrise.chat(f"@{target_username} было выдано предупреждение. ⚠️ В следующий раз следуйте правилам нашей комнаты! За повторное предупреждение срабатывает кик ❗️")
            elif warning_count >= 2:
                await self.highrise.chat(f"@{target_username} получил второе предупреждение и был кикнут из комнаты! ❗️")
                await self.kick_user(target_user.id)
                # Сбрасываем предупреждения после кика
                del WARNINGS[target_user.id]
            
            save_data("warnings.json", WARNINGS)
            
        except Exception as e:
            print(f"Error in warning: {e}")

    async def handle_kick(self, user: User, message: str):
        """Обработка кика пользователя"""
        try:
            # Проверяем права доступа
            if not self.has_full_access(user.id):
                await self.send_whisper(user.id, "Эта команда доступна только владельцу и администраторам!")
                return
            
            target_username = message.replace("кик @", "").strip()
            
            # Ищем пользователя
            room_users = await self.highrise.get_room_users()
            target_user = None
            
            for u, _ in room_users.content:
                if u.username.lower() == target_username.lower():
                    target_user = u
                    break
            
            if not target_user:
                await self.send_whisper(user.id, f"Пользователь @{target_username} не найден в комнате.")
                return
            
            if self.is_moderator(target_user.id):
                await self.send_whisper(user.id, "Нельзя кикнуть модератора!")
                return
            
            await self.kick_user(target_user.id)
            await self.highrise.chat(f"@{target_username} был кикнут из комнаты модератором @{user.username}")
            
        except Exception as e:
            print(f"Error in kick: {e}")

    async def handle_ban(self, user: User, message: str):
        """Обработка бана пользователя"""
        try:
            # Проверяем права доступа
            if not self.has_full_access(user.id):
                await self.send_whisper(user.id, "Эта команда доступна только владельцу и администраторам!")
                return
            
            target_username = message.replace("бан @", "").strip()
            
            # Ищем пользователя
            room_users = await self.highrise.get_room_users()
            target_user = None
            
            for u, _ in room_users.content:
                if u.username.lower() == target_username.lower():
                    target_user = u
                    break
            
            if not target_user:
                await self.send_whisper(user.id, f"Пользователь @{target_username} не найден в комнате.")
                return
            
            if self.is_moderator(target_user.id):
                await self.send_whisper(user.id, "Нельзя забанить модератора!")
                return
            
            await self.ban_user(target_user.id)
            await self.highrise.chat(f"@{target_username} был забанен модератором @{user.username}")
            
        except Exception as e:
            print(f"Error in ban: {e}")

    async def handle_emote_command(self, user: User, message: str):
        """Обработка команды анимации"""
        try:
            emote_input = message.replace("!emote ", "").strip()
            
            emote_id = None
            
            # Ищем по ID
            if emote_input.isdigit():
                emote_num = int(emote_input)
                if 1 <= emote_num <= 228:
                    # Ищем анимацию по номеру
                    for key, data in emotes.items():
                        if data.get("id") == f"emote-{emote_num}":
                            emote_id = data["id"]
                            break
            else:
                # Специальная обработка для ghost float
                if emote_input.lower() in ["гост", "ghost", "ghostfloat"]:
                    emote_id = "emote-ghost-idle"
                else:
                    # Ищем по названию
                    for key, data in emotes.items():
                        if emote_input.lower() == data.get("name", "").lower():
                            emote_id = data["id"]
                            break
            
            if emote_id:
                await self.start_emote_loop(user.id, emote_id)
                await self.send_whisper(user.id, f"Цикличная анимация '{emote_input}' запущена! Напишите '0' или 'стоп' для остановки.")
            else:
                await self.send_whisper(user.id, f"Анимация '{emote_input}' не найдена. Используйте ID (1-228) или название анимации.")
                
        except Exception as e:
            print(f"Error in emote command: {e}")

    async def handle_emote_by_name(self, user: User, message: str):
        """Обработка анимации по названию без команды"""
        try:
            message_lower = message.lower().strip()
            
            emote_id = None
            
            # Специальная обработка для ghost float
            if message_lower in ["гост", "ghost", "ghostfloat"]:
                emote_id = "emote-ghost-idle"
            # Ищем по ID
            elif message in emotes:
                emote_id = emotes[message]["id"]
            else:
                # Ищем по названию (точное совпадение)
                for key, data in emotes.items():
                    if message_lower == data.get("name", "").lower():
                        emote_id = data["id"]
                        break
                
                # Если не найдено, ищем частичное совпадение
                if not emote_id:
                    for key, data in emotes.items():
                        emote_name = data.get("name", "").lower()
                        if message_lower in emote_name or emote_name in message_lower:
                            emote_id = data["id"]
                            break
            
            if emote_id:
                await self.start_emote_loop(user.id, emote_id)
                # print(f"Цикличная анимация '{message}' запущена: {emote_id}")
            # else:
            #     print(f"Анимация '{message}' не найдена")
                
        except Exception as e:
            print(f"Error in emote by name: {e}")

    async def show_message_leaderboard(self, user: User):
        """Показывает топ по сообщениям"""
        try:
            if not MESSAGE_COUNT:
                await self.send_whisper(user.id, "Нет данных о сообщениях.")
                return
            
            # Сортируем по количеству сообщений
            sorted_users = sorted(MESSAGE_COUNT.items(), key=lambda x: x[1]["count"], reverse=True)
            
            top_message = "🏆 Топ по сообщениям:\n"
            for i, (user_id, data) in enumerate(sorted_users[:10], 1):
                username = data["username"]
                count = data["count"]
                top_message += f"{i}. @{username}: {count} сообщений\n"
            
            await self.send_whisper(user.id, top_message)
            
        except Exception as e:
            print(f"Error showing leaderboard: {e}")

    async def show_user_level(self, user: User):
        """Показывает уровень пользователя"""
        try:
            level = self.get_user_level(user.id)
            messages = USER_LEVELS.get(user.id, {}).get("messages", 0)
            required = 100 * level
            
            await self.send_whisper(user.id, f"Ваш уровень: {level}\nСообщений до следующего уровня: {required - messages}/{required}")
            
        except Exception as e:
            print(f"Error showing user level: {e}")

    async def show_user_rights(self, user: User):
        """Показывает права пользователя"""
        try:
            rights_info = f"🔐 Права пользователя @{user.username}:\n"
            rights_info += f"ID: {user.id}\n"
            
            if self.is_owner(user.id):
                rights_info += "👑 Владелец бота\n"
            elif self.is_admin(user.id):
                rights_info += "⚡ Администратор\n"
            elif self.is_moderator(user.id):
                rights_info += "🛡️ Модератор\n"
            
            if self.is_vip(user.id):
                rights_info += "⭐ VIP пользователь\n"
            
            rights_info += f"\nДоступные команды:\n"
            if self.is_owner(user.id):
                rights_info += "• Все команды модерации (пред, кик, бан)\n"
                rights_info += "• Создание точек телепортации (!TPus)\n"
                rights_info += "• Все VIP команды\n"
                rights_info += "• Управление администраторами (!addadmin, !removeadmin)\n"
                rights_info += "• Удаление VIP статуса (!removevip)\n"
                rights_info += "• Пополнение лимитов VIP (!resetvip)\n"
                rights_info += "• Установка VIP зоны (!setvipzone)\n"
                rights_info += "• Установка места дуэли (!setduel)\n"
            elif self.has_full_access(user.id):
                rights_info += "• Все команды модерации (пред, кик, бан)\n"
                rights_info += "• Создание точек телепортации (!TPus)\n"
                rights_info += "• Все VIP команды\n"
            elif self.is_moderator(user.id):
                rights_info += "• Все команды модерации (пред, кик, бан)\n"
                rights_info += "• Создание точек телепортации (!TPus)\n"
                rights_info += "• Все VIP команды\n"
            
            if self.is_vip(user.id):
                rights_info += "• VIP телепортация (вип тп, вип тп @username)\n"
                rights_info += "• VIP пранки\n"
            elif self.is_moderator(user.id):
                rights_info += "• VIP телепортация (вип тп, вип тп @username)\n"
            elif self.has_full_access(user.id):
                rights_info += "• VIP телепортация (вип тп, вип тп @username)\n"
            
            rights_info += "• Все анимации (1-228)\n"
            rights_info += "• Дуэли и браки\n"
            
            await self.send_whisper(user.id, rights_info)
            
        except Exception as e:
            print(f"Error showing user rights: {e}")

    async def add_admin(self, user: User, message: str):
        """Добавляет администратора (только для владельца)"""
        try:
            target_username = message.replace("!addadmin ", "").strip()
            
            # Ищем пользователя в комнате
            room_users = await self.highrise.get_room_users()
            target_user = None
            for u, _ in room_users.content:
                if u.username.lower() == target_username.lower():
                    target_user = u
                    break
            
            if not target_user:
                await self.send_whisper(user.id, f"Пользователь @{target_username} не найден в комнате.")
                return
            
            if target_user.id in ADMIN_IDS:
                await self.send_whisper(user.id, f"@{target_username} уже является администратором.")
                return
            
            # Добавляем в список администраторов
            ADMIN_IDS.append(target_user.id)
            
            # Обновляем конфигурацию
            config = load_config()
            config["admin_ids"] = ADMIN_IDS
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            await self.highrise.chat(f"👑 @{target_username} назначен администратором бота!")
            await self.send_whisper(target_user.id, "Вы были назначены администратором бота! Используйте команду !rights для просмотра доступных команд.")
            
        except Exception as e:
            print(f"Error adding admin: {e}")

    async def remove_admin(self, user: User, message: str):
        """Удаляет администратора (только для владельца)"""
        try:
            target_username = message.replace("!removeadmin ", "").strip()
            
            # Ищем пользователя в комнате
            room_users = await self.highrise.get_room_users()
            target_user = None
            for u, _ in room_users.content:
                if u.username.lower() == target_username.lower():
                    target_user = u
                    break
            
            if not target_user:
                await self.send_whisper(user.id, f"Пользователь @{target_username} не найден в комнате.")
                return
            
            if target_user.id not in ADMIN_IDS:
                await self.send_whisper(user.id, f"@{target_username} не является администратором.")
                return
            
            if target_user.id == OWNER_ID:
                await self.send_whisper(user.id, "Нельзя удалить владельца бота из списка администраторов.")
                return
            
            # Удаляем из списка администраторов
            ADMIN_IDS.remove(target_user.id)
            
            # Обновляем конфигурацию
            config = load_config()
            config["admin_ids"] = ADMIN_IDS
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            await self.highrise.chat(f"👑 @{target_username} больше не является администратором бота.")
            await self.send_whisper(target_user.id, "Вы больше не являетесь администратором бота.")
            
        except Exception as e:
            print(f"Error removing admin: {e}")

    async def remove_vip(self, user: User, message: str):
        """Удаляет VIP статус у пользователя (только для владельца)"""
        try:
            target_username = message.replace("!removevip ", "").strip()
            
            # Ищем пользователя в комнате
            room_users = await self.highrise.get_room_users()
            target_user = None
            for u, _ in room_users.content:
                if u.username.lower() == target_username.lower():
                    target_user = u
                    break
            
            if not target_user:
                await self.send_whisper(user.id, f"Пользователь @{target_username} не найден в комнате.")
                return
            
            if target_user.id not in VIP_USERS:
                await self.send_whisper(user.id, f"@{target_username} не имеет VIP статуса.")
                return
            
            # Удаляем VIP статус
            del VIP_USERS[target_user.id]
            save_data("vip_users.json", VIP_USERS)
            
            await self.highrise.chat(f"👑 @{target_username} больше не имеет VIP статуса.")
            await self.send_whisper(target_user.id, "Ваш VIP статус был удален владельцем бота.")
            
        except Exception as e:
            print(f"Error removing VIP: {e}")

    async def reset_vip_limits(self, user: User, message: str):
        """Пополнение лимитов VIP пользователя (только для владельца)"""
        try:
            if not self.is_owner(user.id):
                await self.send_whisper(user.id, "Эта команда доступна только владельцу!")
                return
            
            target_username = message.replace("!resetvip ", "").strip()
            
            # Ищем пользователя в комнате
            room_users = await self.highrise.get_room_users()
            target_user = None
            for u, _ in room_users.content:
                if u.username.lower() == target_username.lower():
                    target_user = u
                    break
            
            if not target_user:
                await self.send_whisper(user.id, f"Пользователь @{target_username} не найден в комнате.")
                return
            
            if target_user.id not in VIP_USERS:
                await self.send_whisper(user.id, f"@{target_username} не является VIP пользователем.")
                return
            
            # Пополняем лимиты (телепорты людей к себе: 10, пранки: 3)
            old_tp_uses = VIP_USERS[target_user.id].get("tp_uses", 0)
            old_prank_uses = VIP_USERS[target_user.id].get("prank_uses", 0)
            
            # Пополняем счетчики использований
            VIP_USERS[target_user.id]["tp_uses"] = 0
            VIP_USERS[target_user.id]["prank_uses"] = 0
            save_data("vip_users.json", VIP_USERS)
            
            await self.highrise.chat(f"🔄 Лимиты VIP пользователя @{target_username} пополнены!")
            await self.send_whisper(user.id, f"Лимиты @{target_username} пополнены! Было: телепорты людей {old_tp_uses}/10, пранки {old_prank_uses}/3. Стало: 0/10, 0/3")
            
        except Exception as e:
            print(f"Error resetting VIP limits: {e}")
            await self.send_whisper(user.id, "Ошибка при пополнении лимитов VIP.")

    async def set_vip_zone(self, user: User):
        """Устанавливает VIP зону на текущей позиции владельца"""
        try:
            # Получаем текущую позицию пользователя
            room_users = await self.highrise.get_room_users()
            user_pos = None
            
            for u, pos in room_users.content:
                if u.id == user.id:
                    user_pos = pos
                    break
            
            if not user_pos:
                await self.send_whisper(user.id, "Не удалось получить вашу позицию.")
                return
            
            # Обновляем VIP зону
            global VIP_ZONE
            VIP_ZONE = {
                "x": user_pos.x,
                "y": user_pos.y,
                "z": user_pos.z
            }
            
            # Сохраняем в конфигурацию
            config = load_config()
            config["vip_zone"] = VIP_ZONE
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            await self.highrise.chat(f"👑 VIP зона установлена владельцем @{user.username}!")
            await self.send_whisper(user.id, f"VIP зона установлена в координатах ({VIP_ZONE['x']}, {VIP_ZONE['y']}, {VIP_ZONE['z']})")
            
        except Exception as e:
            print(f"Error setting VIP zone: {e}")

    async def handle_create_tp_point(self, user: User, message: str):
        """Обработка создания точки телепортации"""
        try:
            if not self.has_full_access(user.id):
                await self.send_whisper(user.id, "Эта команда доступна только владельцу и администраторам!")
                return
            
            parts = message.replace("!TPus ", "").strip()
            if "," not in parts:
                await self.send_whisper(user.id, "Используйте: !TPus название1,название2,название3")
                return
            
            names = [name.strip().lower() for name in parts.split(",")]
            
            # Получаем текущую позицию пользователя
            room_users = await self.highrise.get_room_users()
            user_pos = None
            
            for u, pos in room_users.content:
                if u.id == user.id:
                    if isinstance(pos, Position):
                        user_pos = pos
                    break
            
            if not user_pos:
                await self.send_whisper(user.id, "Не удалось получить вашу позицию.")
                return
            
            # Сохраняем точку телепортации
            main_name = names[0]
            CUSTOM_TP_POINTS[main_name] = {
                "x": user_pos.x,
                "y": user_pos.y,
                "z": user_pos.z,
                "alternatives": names[1:] if len(names) > 1 else []
            }
            
            save_data("teleport_points.json", CUSTOM_TP_POINTS)
            
            await self.send_whisper(user.id, f"Точка телепортации '{main_name}' создана! Альтернативные названия: {', '.join(names[1:])}")
            
        except Exception as e:
            print(f"Error creating TP point: {e}")

    async def handle_teleport_point(self, user: User, message: str):
        """Обработка телепортации к точке"""
        try:
            message_lower = message.lower()
            
            for point_name, point_data in CUSTOM_TP_POINTS.items():
                all_names = [point_name] + point_data.get("alternatives", [])
                if message_lower in [name.lower() for name in all_names]:
                    await self.teleport_user(user.id, point_data["x"], point_data["y"], point_data["z"])
                    await self.send_whisper(user.id, f"Вы телепортированы в точку '{point_name}'")
                    return
                    
        except Exception as e:
            print(f"Error in teleport point: {e}")

    async def on_tip(self, sender: User, receiver: User, tip: CurrencyItem | Item) -> None:
        """Обработка чаевых"""
        try:
            if receiver.id == self.bot_id:  # Чаевые боту
                amount = tip.amount if hasattr(tip, 'amount') else 0
                
                # Инициализируем накопления пользователя
                if sender.id not in VIP_SAVINGS:
                    VIP_SAVINGS[sender.id] = {"amount": 0, "username": sender.username}
                
                # Добавляем к накоплениям
                VIP_SAVINGS[sender.id]["amount"] += amount
                VIP_SAVINGS[sender.id]["username"] = sender.username
                
                current_savings = VIP_SAVINGS[sender.id]["amount"]
                
                # Обработка VIP покупки
                if current_savings >= VIP_PRICE_MONTHLY:
                    months = current_savings // VIP_PRICE_MONTHLY
                    remaining = current_savings % VIP_PRICE_MONTHLY
                    
                    if sender.id in VIP_USERS:
                        # Продлеваем VIP
                        VIP_USERS[sender.id]["expires"] += timedelta(days=30 * months)
                    else:
                        # Новый VIP
                        VIP_USERS[sender.id] = {
                            "expires": datetime.now() + timedelta(days=30 * months),
                            "tp_uses": 0,
                            "prank_uses": 0
                        }
                    
                    # Обновляем накопления
                    VIP_SAVINGS[sender.id]["amount"] = remaining
                    
                    save_data("vip_users.json", VIP_USERS)
                    save_data("vip_savings.json", VIP_SAVINGS)
                    
                    if remaining > 0:
                        await self.highrise.chat(f"🌟 @{sender.username} приобрел VIP статус на {months} месяц(ев)! Остаток: {remaining}г")
                    else:
                        await self.highrise.chat(f"🌟 @{sender.username} приобрел VIP статус на {months} месяц(ев)! Поздравляем!")
                else:
                    # Недостаточно для VIP
                    needed = VIP_PRICE_MONTHLY - current_savings
                    await self.highrise.chat(f"💰 @{sender.username} накопил {current_savings}г из {VIP_PRICE_MONTHLY}г для VIP. Осталось: {needed}г")
                    save_data("vip_savings.json", VIP_SAVINGS)
                
                
                # Обработка оплаты развода
                if amount == MARRIAGE_DIVORCE_COST and sender.id in MARRIAGES:
                    partner_id = MARRIAGES[sender.id]["partner"]
                    
                    # Ищем имя партнера
                    partner_name = "Unknown"
                    for uid, data in MESSAGE_COUNT.items():
                        if uid == partner_id:
                            partner_name = data["username"]
                            break
                    
                    # Увеличиваем счетчик разводов
                    if sender.id not in DIVORCE_COUNT:
                        DIVORCE_COUNT[sender.id] = {"count": 0}
                    DIVORCE_COUNT[sender.id]["count"] += 1
                    
                    del MARRIAGES[sender.id]
                    del MARRIAGES[partner_id]
                    save_data("marriages.json", MARRIAGES)
                    save_data("divorce_count.json", DIVORCE_COUNT)
                    
                    await self.highrise.chat(f"Брак между @{sender.username} и @{partner_name} был расторгнут 💔")
                
        except Exception as e:
            print(f"Error in tip handler: {e}")

    async def show_bot_info(self, user: User):
        """Показывает информацию о боте"""
        try:
            # Получаем время работы бота
            uptime = datetime.now() - self.start_time if hasattr(self, 'start_time') else timedelta(0)
            days = uptime.days
            hours = uptime.seconds // 3600
            minutes = (uptime.seconds % 3600) // 60
            seconds = uptime.seconds % 60
            
            # Форматируем время работы
            if days > 0:
                uptime_str = f"{days}д, {hours}ч, {minutes}м, {seconds}с"
            elif hours > 0:
                uptime_str = f"{hours}ч, {minutes}м, {seconds}с"
            elif minutes > 0:
                uptime_str = f"{minutes}м, {seconds}с"
            else:
                uptime_str = f"{seconds}с"
            
            # Получаем статистику VIP пользователей
            vip_count = len(VIP_USERS)
            total_users = len(MESSAGE_COUNT)
            
            # Получаем статистику браков
            marriage_count = len(MARRIAGES) // 2  # Делим на 2, так как брак записан дважды
            
            # Формируем информацию о боте
            info = f"🤖 **Информация о боте:**\n"
            info += f"📛 **Имя:** TestGlux BOT\n"
            info += f"🔧 **Статус:** Бот\n"
            info += f"👑 **Уровень:** Администратор\n"
            info += f"📊 **Пользователей:** {total_users}\n"
            info += f"⭐ **VIP пользователей:** {vip_count}\n"
            info += f"💍 **Активных браков:** {marriage_count}\n"
            info += f"📅 **Дата запуска:** {self.start_time.strftime('%Y-%m-%d %H:%M:%S') if hasattr(self, 'start_time') else 'Неизвестно'}\n"
            info += f"⏱️ **Время работы:** {uptime_str}\n"
            info += f"🎮 **Команды:** !info, !rights, вип, пранк, дуэль, брак"
            
            await self.send_whisper(user.id, info)
            
        except Exception as e:
            print(f"Error showing bot info: {e}")
            await self.send_whisper(user.id, "Ошибка при получении информации о боте.")

    async def set_duel_location(self, user: User):
        """Устанавливает место для дуэлей (только для владельца)"""
        try:
            if not self.is_owner(user.id):
                await self.send_whisper(user.id, "Эта команда доступна только владельцу бота.")
                return
            
            # Получаем позицию владельца
            room_users = await self.highrise.get_room_users()
            owner_pos = None
            for u, pos in room_users.content:
                if u.id == user.id:
                    if isinstance(pos, Position):
                        owner_pos = pos
                    break
            
            if not owner_pos:
                await self.send_whisper(user.id, "Не удалось получить вашу позицию.")
                return
            
            # Сохраняем место дуэли в конфигурации
            global DUEL_LOCATION
            DUEL_LOCATION = {
                "x": owner_pos.x,
                "y": owner_pos.y,
                "z": owner_pos.z,
                "facing": owner_pos.facing
            }
            
            # Обновляем конфигурацию
            config = load_config()
            config["duel_location"] = DUEL_LOCATION
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            await self.highrise.chat(f"🎯 Место для дуэлей установлено владельцем @{user.username}!")
            await self.send_whisper(user.id, f"Место дуэли установлено: x={owner_pos.x}, y={owner_pos.y}, z={owner_pos.z}")
            
        except Exception as e:
            print(f"Error setting duel location: {e}")
            await self.send_whisper(user.id, "Ошибка при установке места дуэли.")
    
    async def show_user_info(self, user: User):
        """Показывает информацию о пользователе"""
        try:
            user_id = user.id
            username = user.username
            
            # Получаем профиль пользователя
            profile = USER_PROFILES.get(user_id, {})
            
            # Получаем VIP статус и лимиты
            is_vip = self.is_vip(user_id)
            vip_data = VIP_USERS.get(user_id, {})
            tp_uses = vip_data.get("tp_uses", 0) if is_vip else 0
            prank_uses = vip_data.get("prank_uses", 0) if is_vip else 0
            
            # Получаем уровень пользователя
            level_data = USER_LEVELS.get(user_id, {})
            level = level_data.get("level", 1)
            messages = level_data.get("messages", 0)
            
            # Получаем количество предупреждений
            warnings = WARNINGS.get(user_id, {})
            warning_count = warnings.get("count", 0)
            
            # Получаем количество разводов
            divorce_count = DIVORCE_COUNT.get(user_id, {}).get("count", 0)
            
            # Формируем сообщение
            info_message = f"📋 Информация о @{username}:\n\n"
            
            # Основная информация
            if profile:
                info_message += f"🔹 Био: {profile.get('bio', 'Не указано')}\n"
                info_message += f"🔹 Дата регистрации: {profile.get('joined_at', 'Неизвестно')}\n"
                info_message += f"🔹 Подписчики: {profile.get('num_followers', 0)}\n"
                info_message += f"🔹 Подписки: {profile.get('num_following', 0)}\n"
                info_message += f"🔹 Друзья: {profile.get('num_friends', 0)}\n"
                info_message += f"🔹 Команда: {profile.get('crew', 'Нет команды')}\n"
                info_message += f"🔹 Последний раз онлайн: {profile.get('last_seen', 'Неизвестно')}\n"
            else:
                info_message += "🔹 Профиль: Не загружен\n"
            
            # Игровая статистика
            info_message += f"\n🎮 Игровая статистика:\n"
            info_message += f"🔹 Уровень: {level}\n"
            info_message += f"🔹 Сообщений: {messages}\n"
            info_message += f"🔹 Предупреждений: {warning_count}\n"
            info_message += f"🔹 Разводов: {divorce_count}\n"
            
            # VIP статус
            if is_vip:
                info_message += f"\n⭐ VIP статус:\n"
                info_message += f"🔹 Телепортов осталось: {10 - tp_uses}\n"
                info_message += f"🔹 Пранков осталось: {5 - prank_uses}\n"
                tp_to_self_uses = vip_data.get("tp_to_self_uses", 0)
                info_message += f"🔹 Телепортов к себе осталось: {10 - tp_to_self_uses}\n"
                
                if vip_data.get("expires"):
                    expires = vip_data["expires"]
                    if isinstance(expires, str):
                        expires = datetime.fromisoformat(expires.replace('Z', '+00:00'))
                    
                    current_time = datetime.now()
                    time_left = expires - current_time
                    
                    if time_left.total_seconds() > 0:
                        # Вычисляем дни, часы, минуты, секунды
                        days = time_left.days
                        hours = time_left.seconds // 3600
                        minutes = (time_left.seconds % 3600) // 60
                        seconds = time_left.seconds % 60
                        
                        # Формируем сообщение о времени
                        time_parts = []
                        if days > 0:
                            time_parts.append(f"{days} дн")
                        if hours > 0:
                            time_parts.append(f"{hours} ч")
                        if minutes > 0:
                            time_parts.append(f"{minutes} мин")
                        if seconds > 0 or not time_parts:
                            time_parts.append(f"{seconds} сек")
                        
                        time_left_str = " ".join(time_parts)
                        info_message += f"🔹 VIP истекает через: {time_left_str}\n"
                    else:
                        info_message += f"🔹 VIP истек\n"
            else:
                info_message += f"\n⭐ VIP статус: Не VIP\n"
            
            # Роли
            roles = []
            if self.is_owner(user_id):
                roles.append("Владелец")
            elif self.is_admin(user_id):
                roles.append("Администратор")
            elif self.is_moderator(user_id):
                roles.append("Модератор")
            
            if roles:
                info_message += f"\n👑 Роли: {', '.join(roles)}\n"
            
            # Отправляем сообщение
            await self.send_whisper(user_id, info_message)
            
        except Exception as e:
            print(f"Ошибка при показе информации о пользователе: {e}")
            await self.highrise.send_whisper(user.id, "❌ Ошибка при получении информации")
    
    async def teleport_bot_to_owner(self, user: User):
        """Телепортирует бота к владельцу"""
        try:
            if not self.is_owner(user.id):
                await self.send_whisper(user.id, "Эта команда доступна только владельцу бота.")
                return
            
            # Получаем позицию владельца
            room_users = await self.highrise.get_room_users()
            owner_pos = None
            for u, pos in room_users.content:
                if u.id == user.id:
                    if isinstance(pos, Position):
                        owner_pos = pos
                    break
            
            if not owner_pos:
                await self.send_whisper(user.id, "Не удалось получить вашу позицию.")
                return
            
            # Телепортируем бота к владельцу
            await self.highrise.teleport(self.bot_id, owner_pos)
            
            await self.highrise.chat(f"🤖 Бот телепортирован к владельцу @{user.username}!")
            await self.send_whisper(user.id, f"Бот успешно телепортирован к вам: x={owner_pos.x}, y={owner_pos.y}, z={owner_pos.z}")
            
        except Exception as e:
            print(f"Ошибка при телепортации бота: {e}")
            await self.send_whisper(user.id, "❌ Ошибка при телепортации бота")
    
    async def handle_tp_to_self(self, user: User):
        """Телепортирует пользователя к себе"""
        try:
            # Проверяем права доступа: VIP, модераторы, администраторы, владелец
            if not (self.is_vip(user.id) or self.is_moderator(user.id) or self.has_full_access(user.id)):
                await self.send_whisper(user.id, "Эта команда доступна только VIP пользователям, модераторам и администраторам!")
                return
            
            # Получаем позицию пользователя
            room_users = await self.highrise.get_room_users()
            user_pos = None
            for u, pos in room_users.content:
                if u.id == user.id:
                    if isinstance(pos, Position):
                        user_pos = pos
                    break
            
            if not user_pos:
                await self.send_whisper(user.id, "Не удалось получить вашу позицию.")
                return
            
            # Телепортируем пользователя к себе (на ту же позицию)
            await self.teleport_user(user.id, user_pos.x, user_pos.y, user_pos.z)
            
            await self.send_whisper(user.id, f"Вы телепортированы к себе: x={user_pos.x}, y={user_pos.y}, z={user_pos.z}")
            
        except Exception as e:
            print(f"Ошибка при телепортации к себе: {e}")
            await self.send_whisper(user.id, "❌ Ошибка при телепортации к себе")

    async def handle_tp_player_to_self(self, user: User, message: str):
        """Телепортирует указанного игрока к себе"""
        print(f"Выполняется handle_tp_player_to_self: {message}")
        try:
            if not (self.is_vip(user.id) or self.is_moderator(user.id) or self.has_full_access(user.id)):
                await self.send_whisper(user.id, "Эта команда доступна только VIP пользователям, модераторам и администраторам!")
                return
            
            # Извлекаем имя игрока из сообщения
            target_username = message.replace("тп @", "").strip()
            if not target_username:
                await self.send_whisper(user.id, "Использование: тп @username")
                return
            
            if target_username.startswith("@"):
                target_username = target_username[1:]
            
            # Получаем позицию пользователя, который использует команду
            room_users = await self.highrise.get_room_users()
            user_pos = None
            target_user = None
            
            for u, pos in room_users.content:
                if u.id == user.id:
                    if isinstance(pos, Position):
                        user_pos = pos
                elif u.username.lower() == target_username.lower():
                    target_user = u
            
            if not user_pos:
                await self.send_whisper(user.id, "Не удалось получить вашу позицию.")
                return
            
            if not target_user:
                await self.send_whisper(user.id, f"Пользователь @{target_username} не найден в комнате.")
                return
            
            # Телепортируем игрока к себе
            await self.teleport_user(target_user.id, user_pos.x, user_pos.y, user_pos.z)
            await self.send_whisper(user.id, f"@{target_user.username} телепортирован к вам: x={user_pos.x}, y={user_pos.y}, z={user_pos.z}")
            await self.send_whisper(target_user.id, f"Вы телепортированы к @{user.username}")
            
        except Exception as e:
            print(f"Ошибка при телепортации игрока к себе: {e}")
            await self.send_whisper(user.id, "❌ Ошибка при телепортации игрока к себе")

    async def handle_tp_to_player(self, user: User, message: str):
        """Телепортирует вас к указанному игроку"""
        try:
            # Извлекаем имя игрока из сообщения
            target_username = message.replace("к @", "").strip()
            if not target_username:
                await self.send_whisper(user.id, "Использование: к @username")
                return
            
            if target_username.startswith("@"):
                target_username = target_username[1:]
            
            # Ищем игрока в комнате
            room_users = await self.highrise.get_room_users()
            target_user = None
            target_pos = None
            
            for u, pos in room_users.content:
                if u.username.lower() == target_username.lower():
                    target_user = u
                    if isinstance(pos, Position):
                        target_pos = pos
                    break
            
            if not target_user:
                await self.send_whisper(user.id, f"Пользователь @{target_username} не найден в комнате.")
                return
            
            if not target_pos:
                await self.send_whisper(user.id, f"Не удалось получить позицию @{target_username}.")
                return
            
            # Телепортируем к игроку
            await self.teleport_user(user.id, target_pos.x, target_pos.y, target_pos.z)
            await self.send_whisper(user.id, f"Вы телепортированы к @{target_user.username}: x={target_pos.x}, y={target_pos.y}, z={target_pos.z}")
            
        except Exception as e:
            print(f"Ошибка при телепортации к игроку: {e}")
            await self.send_whisper(user.id, "❌ Ошибка при телепортации к игроку")

    async def handle_tp_coords(self, user: User, message: str):
        """Телепорт по координатам"""
        try:
            if not (self.is_vip(user.id) or self.is_moderator(user.id) or self.has_full_access(user.id)):
                await self.send_whisper(user.id, "Эта команда доступна только VIP пользователям, модераторам и администраторам!")
                return
            
            # Извлекаем координаты из сообщения
            coords = message.replace("тпк ", "").strip().split()
            if len(coords) != 3:
                await self.send_whisper(user.id, "Использование: тпк x y z")
                return
            
            try:
                x = float(coords[0])
                y = float(coords[1])
                z = float(coords[2])
            except ValueError:
                await self.send_whisper(user.id, "Координаты должны быть числами!")
                return
            
            # Телепортируем пользователя
            await self.teleport_user(user.id, x, y, z)
            await self.send_whisper(user.id, f"Вы телепортированы: x={x}, y={y}, z={z}")
            
        except Exception as e:
            print(f"Ошибка при телепорте по координатам: {e}")
            await self.send_whisper(user.id, "❌ Ошибка при телепорте по координатах")

    async def handle_tp_to_self_limited(self, user: User):
        """Телепортирует пользователя к себе с лимитами"""
        try:
            if not (self.is_vip(user.id) or self.is_moderator(user.id) or self.has_full_access(user.id)):
                await self.send_whisper(user.id, "Эта команда доступна только VIP пользователям, модераторам и администраторам!")
                return
            
            # Получаем позицию пользователя
            room_users = await self.highrise.get_room_users()
            user_pos = None
            for u, pos in room_users.content:
                if u.id == user.id:
                    if isinstance(pos, Position):
                        user_pos = pos
                    break
            
            if not user_pos:
                await self.send_whisper(user.id, "Не удалось получить вашу позицию.")
                return
            
            # Проверяем лимиты только для VIP (не модераторов)
            if self.is_vip(user.id) and not self.is_moderator(user.id) and not self.has_full_access(user.id):
                # Инициализируем счетчик если его нет
                if user.id not in VIP_USERS:
                    VIP_USERS[user.id] = {
                        "expires": datetime.now() + timedelta(days=30),
                        "tp_uses": 0,
                        "prank_uses": 0,
                        "tp_to_self_uses": 0,
                        "last_tp_to_self_reset": datetime.now()
                    }
                
                # Проверяем, нужно ли сбросить счетчик (новый день)
                last_reset = VIP_USERS[user.id].get("last_tp_to_self_reset")
                if isinstance(last_reset, str):
                    last_reset = datetime.fromisoformat(last_reset.replace('Z', '+00:00'))
                
                current_time = datetime.now()
                if (current_time - last_reset).days >= 1:
                    # Сбрасываем счетчик на новый день
                    VIP_USERS[user.id]["tp_to_self_uses"] = 0
                    VIP_USERS[user.id]["last_tp_to_self_reset"] = current_time
                
                # Проверяем лимит
                if VIP_USERS[user.id]["tp_to_self_uses"] >= 10:
                    await self.send_whisper(user.id, "Вы исчерпали лимит телепортов к себе на сегодня (10/10)! Попробуйте завтра.")
                    return
                
                # Увеличиваем счетчик
                VIP_USERS[user.id]["tp_to_self_uses"] += 1
                save_data("vip_users.json", VIP_USERS)
                
                # Телепортируем пользователя
                await self.teleport_user(user.id, user_pos.x, user_pos.y, user_pos.z)
                
                uses_left = 10 - VIP_USERS[user.id]["tp_to_self_uses"]
                await self.send_whisper(user.id, f"Вы телепортированы к себе: x={user_pos.x}, y={user_pos.y}, z={user_pos.z}\nОсталось использований: {uses_left}/10")
            
            else:
                # Для модераторов и администраторов - без лимитов
                await self.teleport_user(user.id, user_pos.x, user_pos.y, user_pos.z)
                await self.send_whisper(user.id, f"Вы телепортированы к себе: x={user_pos.x}, y={user_pos.y}, z={user_pos.z} (Бесконечные телепорты)")
            
        except Exception as e:
            print(f"Ошибка при телепортации к себе: {e}")
            await self.send_whisper(user.id, "❌ Ошибка при телепортации к себе")
    
    async def add_moderator(self, user: User, message: str):
        """Добавляет модератора и автоматически дает VIP"""
        global MODERATOR_IDS, VIP_USERS
        try:
            if not self.is_owner(user.id):
                await self.send_whisper(user.id, "Эта команда доступна только владельцу бота.")
                return
            
            # Извлекаем имя пользователя из команды
            target_username = message.replace("!addmod ", "").strip()
            if not target_username:
                await self.send_whisper(user.id, "Использование: !addmod @username")
                return
            
            # Убираем @ если есть
            if target_username.startswith("@"):
                target_username = target_username[1:]
            
            # Ищем пользователя в комнате
            room_users = await self.highrise.get_room_users()
            target_user = None
            for u, _ in room_users.content:
                if u.username.lower() == target_username.lower():
                    target_user = u
                    break
            
            if not target_user:
                await self.send_whisper(user.id, f"Пользователь @{target_username} не найден в комнате.")
                return
            
            # Проверяем, не является ли уже модератором
            if target_user.id in MODERATOR_IDS:
                await self.send_whisper(user.id, f"@{target_user.username} уже является модератором.")
                return
            
            # Добавляем в список модераторов
            MODERATOR_IDS.append(target_user.id)
            
            # Обновляем конфигурацию
            config = load_config()
            config["moderator_ids"] = MODERATOR_IDS
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            # Автоматически даем VIP статус модератору
            VIP_USERS[target_user.id] = {
                "expires": datetime.now() + timedelta(days=365),  # VIP на год
                "tp_uses": 0,
                "prank_uses": 0
            }
            save_data("vip_users.json", VIP_USERS)
            
            # Уведомляем всех
            await self.highrise.chat(f"🛡️ @{target_user.username} назначен модератором!")
            await self.send_whisper(user.id, f"Модератор @{target_user.username} добавлен и получил VIP статус на год.")
            await self.send_whisper(target_user.id, f"Поздравляем! Вы назначены модератором и получили VIP статус на год! 🎉")
            
        except Exception as e:
            print(f"Ошибка при добавлении модератора: {e}")
            await self.send_whisper(user.id, "❌ Ошибка при добавлении модератора")

    async def handle_emote_to_player_by_id(self, user: User, message: str):
        """Включает анимацию по ID другому игроку"""
        try:
            # Парсим сообщение: "ID @username"
            parts = message.split()
            if len(parts) != 2:
                await self.send_whisper(user.id, "Использование: ID @username")
                return
            
            emote_id = parts[0].strip()
            target_username = parts[1].replace("@", "").strip()
            
            if not target_username:
                await self.send_whisper(user.id, "Использование: ID @username")
                return
            
            # Проверяем, что ID анимации существует
            emote_found = False
            emote_name = ""
            actual_emote_id = ""
            
            # Сначала проверяем, есть ли такой ключ в словаре
            if emote_id in emotes:
                emote_found = True
                emote_name = emotes[emote_id].get("name", "Неизвестная анимация")
                actual_emote_id = emotes[emote_id].get("id", emote_id)
            else:
                # Если нет, ищем по полному ID
                for key, data in emotes.items():
                    if data.get("id") == emote_id:
                        emote_found = True
                        emote_name = data.get("name", "Неизвестная анимация")
                        actual_emote_id = data.get("id", emote_id)
                        break
            
            if not emote_found:
                await self.send_whisper(user.id, f"Анимация с ID '{emote_id}' не найдена.")
                return
            
            # Ищем пользователя в комнате
            room_users = await self.highrise.get_room_users()
            target_user = None
            for u, _ in room_users.content:
                if u.username.lower() == target_username.lower():
                    target_user = u
                    break
            
            if not target_user:
                await self.send_whisper(user.id, f"Пользователь @{target_username} не найден в комнате.")
                return
            
            # Включаем анимацию другому игроку
            await self.highrise.send_emote(actual_emote_id, target_user.id)
            await self.send_whisper(user.id, f"Анимация '{emote_name}' (ID: {emote_id}) включена для @{target_user.username}!")
            
        except Exception as e:
            print(f"Ошибка при включении анимации по ID: {e}")
            await self.send_whisper(user.id, "❌ Ошибка при включении анимации")

    async def handle_emote_to_player_by_name(self, user: User, message: str):
        """Включает анимацию по названию другому игроку"""
        try:
            # Парсим сообщение: "название @username"
            parts = message.split()
            if len(parts) < 3:
                await self.send_whisper(user.id, "Использование: название @username")
                return
            
            # Извлекаем название анимации (все слова кроме последнего)
            emote_name = " ".join(parts[:-1])
            target_username = parts[-1].replace("@", "").strip()
            
            if not target_username:
                await self.send_whisper(user.id, "Использование: название @username")
                return
            
            # Ищем пользователя в комнате
            room_users = await self.highrise.get_room_users()
            target_user = None
            for u, _ in room_users.content:
                if u.username.lower() == target_username.lower():
                    target_user = u
                    break
            
            if not target_user:
                await self.send_whisper(user.id, f"Пользователь @{target_username} не найден в комнате.")
                return
            
            # Ищем анимацию по названию
            emote_id = None
            message_lower = emote_name.lower().strip()
            
            for key, data in emotes.items():
                if data.get("name", "").lower() == message_lower:
                    emote_id = data.get("id")
                    break
            
            if not emote_id:
                await self.send_whisper(user.id, f"Анимация '{emote_name}' не найдена.")
                return
            
            # Включаем анимацию другому игроку
            await self.highrise.send_emote(emote_id, target_user.id)
            await self.send_whisper(user.id, f"Анимация '{emote_name}' включена для @{target_user.username}!")
            
        except Exception as e:
            print(f"Ошибка при включении анимации по названию: {e}")
            await self.send_whisper(user.id, "❌ Ошибка при включении анимации")

    async def set_bot_spawn_position(self, user: User):
        """Устанавливает позицию спавна бота"""
        try:
            # Получаем позицию владельца
            room_users = await self.highrise.get_room_users()
            owner_pos = None
            
            for u, pos in room_users.content:
                if u.id == user.id:
                    if isinstance(pos, Position):
                        owner_pos = pos
                    break
            
            if not owner_pos:
                await self.send_whisper(user.id, "Не удалось получить вашу позицию.")
                return
            
            # Сохраняем позицию бота
            global BOT_SPAWN_POSITION
            BOT_SPAWN_POSITION = {
                "x": owner_pos.x,
                "y": owner_pos.y,
                "z": owner_pos.z,
                "facing": "FrontLeft"  # По умолчанию
            }
            
            # Сохраняем в файл
            save_data("bot_spawn_position.json", BOT_SPAWN_POSITION)
            
            await self.send_whisper(user.id, f"✅ Позиция спавна бота установлена: x={owner_pos.x}, y={owner_pos.y}, z={owner_pos.z}")
            print(f"Позиция спавна бота установлена владельцем: {BOT_SPAWN_POSITION}")
            
        except Exception as e:
            print(f"Ошибка при установке позиции спавна бота: {e}")
            await self.send_whisper(user.id, "❌ Ошибка при установке позиции спавна бота")

    async def teleport_bot_to_spawn_position(self):
        """Телепортирует бота на сохраненную позицию спавна"""
        try:
            global BOT_SPAWN_POSITION
            
            if not BOT_SPAWN_POSITION:
                print("Позиция спавна бота не установлена, бот остается на месте")
                return
            
            x = BOT_SPAWN_POSITION.get("x", 0)
            y = BOT_SPAWN_POSITION.get("y", 0)
            z = BOT_SPAWN_POSITION.get("z", 0)
            
            # Телепортируем бота
            await self.highrise.teleport(user_id=self.bot_id, dest=Position(x, y, z))
            print(f"Бот телепортирован на позицию спавна: x={x}, y={y}, z={z}")
            
        except Exception as e:
            print(f"Ошибка при телепортации бота на позицию спавна: {e}")

    async def handle_flirt_command(self, user: User, message: str):
        """Обработка команды флирта"""
        try:
            # Парсим сообщение: "!flirt @username"
            target_username = message.replace("!flirt @", "").strip()
            
            if not target_username:
                await self.send_whisper(user.id, "Использование: !flirt @username")
                return
            
            # Ищем пользователя в комнате
            room_users = await self.highrise.get_room_users()
            target_user = None
            target_pos = None
            user_pos = None
            
            for u, pos in room_users.content:
                if u.id == user.id:
                    if isinstance(pos, Position):
                        user_pos = pos
                elif u.username.lower() == target_username.lower():
                    target_user = u
                    if isinstance(pos, Position):
                        target_pos = pos
            
            if not target_user:
                await self.send_whisper(user.id, f"Пользователь @{target_username} не найден в комнате.")
                return
            
            if not user_pos or not target_pos:
                await self.send_whisper(user.id, "Не удалось получить позиции игроков.")
                return
            
            if target_user.id == user.id:
                await self.send_whisper(user.id, "Нельзя флиртовать с самим собой!")
                return
            
            # Проверяем расстояние между игроками
            dx = target_pos.x - user_pos.x
            dz = target_pos.z - user_pos.z
            distance = (dx**2 + dz**2)**0.5  # Евклидово расстояние в 2D
            
            if distance > 3.0:
                await self.send_whisper(user.id, f"@{target_user.username} слишком далеко! Подойдите ближе (максимум 3 блока).")
                return
            
            # Вычисляем направление для поворота друг к другу
            
            # Определяем направление взгляда для каждого игрока
            user_facing = self.calculate_facing_direction(dx, dz)
            target_facing = self.calculate_facing_direction(-dx, -dz)
            
            # Поворачиваем игроков друг к другу
            await self.highrise.teleport(user_id=user.id, dest=Position(user_pos.x, user_pos.y, user_pos.z, facing=user_facing))
            await self.highrise.teleport(user_id=target_user.id, dest=Position(target_pos.x, target_pos.y, target_pos.z, facing=target_facing))
            
            # Небольшая пауза для поворота
            await asyncio.sleep(0.5)
            
            # Включаем анимацию поцелуя для обоих игроков
            await self.highrise.send_emote("emote-kissing", user.id)
            await self.highrise.send_emote("emote-kissing", target_user.id)
            
            # Отправляем сообщение в чат
            await self.highrise.chat(f"💕 @{user.username} и @{target_user.username} флиртуют друг с другом!")
            
            # Отправляем подтверждение участникам
            await self.send_whisper(user.id, f"Вы флиртуете с @{target_user.username}!")
            await self.send_whisper(target_user.id, f"@{user.username} флиртует с вами!")
            
        except Exception as e:
            print(f"Ошибка при выполнении команды флирта: {e}")
            await self.send_whisper(user.id, "❌ Ошибка при выполнении команды флирта")

    def calculate_facing_direction(self, dx: float, dz: float) -> str:
        """Вычисляет направление взгляда на основе разности координат"""
        if abs(dx) > abs(dz):
            if dx > 0:
                return "FrontRight"
            else:
                return "FrontLeft"
        else:
            if dz > 0:
                return "FrontLeft"
            else:
                return "FrontRight"

    async def handle_wish_command(self, user: User, message: str):
        """Обработка команды пожеланий и предложений"""
        try:
            # Парсим сообщение: "!wish текст пожелания"
            wish_text = message.replace("!wish ", "").strip()
            
            if not wish_text:
                await self.send_whisper(user.id, "Использование: !wish ваше пожелание или предложение")
                return
            
            if len(wish_text) < 5:
                await self.send_whisper(user.id, "Пожелание должно содержать минимум 5 символов.")
                return
            
            if len(wish_text) > 500:
                await self.send_whisper(user.id, "Пожелание слишком длинное (максимум 500 символов).")
                return
            
            # Создаем запись о пожелании
            wish_entry = {
                "user": user.id,
                "username": user.username,
                "message": wish_text,
                "timestamp": str(datetime.now())
            }
            
            # Добавляем в список пожеланий
            global WISHES_SUGGESTIONS
            WISHES_SUGGESTIONS.append(wish_entry)
            
            # Сохраняем в файл
            save_data("wishes_suggestions.json", WISHES_SUGGESTIONS)
            
            # Отправляем подтверждение пользователю
            await self.send_whisper(user.id, f"✅ Ваше пожелание сохранено! Спасибо за обратную связь, @{user.username}!")
            
            # Отправляем уведомление владельцу
            if self.is_owner(user.id):
                await self.send_whisper(user.id, "📝 Пожелание также отправлено владельцу бота.")
            else:
                await self.send_whisper(OWNER_ID, f"💌 Новое пожелание от @{user.username}: {wish_text}")
            
            print(f"Новое пожелание от {user.username}: {wish_text}")
            
        except Exception as e:
            print(f"Ошибка при сохранении пожелания: {e}")
            await self.send_whisper(user.id, "❌ Ошибка при сохранении пожелания. Попробуйте позже.")

def signal_handler(sig, frame):
    """Обработчик сигнала завершения"""
    print("\nПолучен сигнал завершения. Сохраняем данные...")
    
    # Останавливаем все активные анимации
    global ACTIVE_ANIMATIONS
    for user_id in list(ACTIVE_ANIMATIONS.keys()):
        if ACTIVE_ANIMATIONS[user_id]["task"]:
            ACTIVE_ANIMATIONS[user_id]["task"].cancel()
    ACTIVE_ANIMATIONS.clear()
    print("Все активные анимации остановлены.")
    
    save_data("marriages.json", MARRIAGES)
    save_data("divorce_count.json", DIVORCE_COUNT)
    save_data("warnings.json", WARNINGS)
    save_data("vip_users.json", VIP_USERS)
    save_data("user_levels.json", USER_LEVELS)
    save_data("message_count.json", MESSAGE_COUNT)
    save_data("teleport_points.json", CUSTOM_TP_POINTS)
    save_data("vip_savings.json", VIP_SAVINGS)
    save_data("user_profiles.json", USER_PROFILES)
    save_data("bot_spawn_position.json", BOT_SPAWN_POSITION)
    save_data("wishes_suggestions.json", WISHES_SUGGESTIONS)
    print("Данные сохранены. Завершение работы.")
    sys.exit(0)

# Регистрируем обработчики сигналов
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Добавляем импорты для запуска
from highrise.__main__ import BotDefinition
from asyncio import run as arun

# Функция запуска бота
async def run_bot(room_id: str, api_key: str) -> None:
    """Запускает бота"""
    definitions = [BotDefinition(Bot(), room_id, api_key)]
    from highrise import __main__
    await __main__.main(definitions)

# Запуск бота при выполнении файла
if __name__ == "__main__":
    # Загружаем конфигурацию
    config = load_config()
    room_id = config.get("room_id", "668bc58d2aa6dd7d3bc16037")
    api_key = config.get("bot_token", "0288f3080eaaf24ce8748445f623737bebbbea63db35fbbd8ec0371ffc5840f6")
    
    # Устанавливаем переменные окружения
    import os
    os.environ['ROOM_ID'] = room_id
    os.environ['API_TOKEN'] = api_key
    os.environ['HIGHRISE_ROOM_ID'] = room_id
    os.environ['HIGHRISE_API_TOKEN'] = api_key
    
    print("=" * 50)
    print("Запуск Highrise бота")
    print("=" * 50)
    print(f"Room ID: {room_id}")
    print(f"API Key: {api_key[:10]}...")
    print("=" * 50)
    
    try:
        arun(run_bot(room_id, api_key))
    except KeyboardInterrupt:
        print("\nБот остановлен пользователем")
    except Exception as e:
        print(f"\nОшибка запуска бота: {e}")
        print("Попробуйте перезапустить бота...")
        input("Нажмите Enter для выхода...") 