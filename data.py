from dataclasses import dataclass
import os
import json
import requests
import math
from typing import Any, Dict
from datetime import datetime, timedelta
from enum import IntEnum, unique


def parse_timestamp(timestamp):
    timestamp = timestamp.replace("Z", "+00:00")
    return datetime.fromisoformat(timestamp)


def format_timestamp(dt: datetime):
    return dt.isoformat()


def offset_timestamp(timestamp: str, delta_secs: float) -> str:
    dt = parse_timestamp(timestamp)
    dt = dt + timedelta(seconds=delta_secs)
    timestamp = format_timestamp(dt)
    return timestamp.replace("+00:00", "Z")


cache = {}


def get_cached(key, url):
    key = key.replace(":", "_")
    if key in cache:
        return cache[key]

    path = os.path.join("cache", key + ".json")
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                cache[key] = data
                return data
            except json.JSONDecodeError:
                pass

    data = requests.get(url).json()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)
    cache[key] = data
    return data


def get_mods(entity):
    return (
        entity.get("permAttr", [])
        + entity.get("seasAttr", [])
        + entity.get("weekAttr", [])
        + entity.get("gameAttr", [])
        + entity.get("itemAttr", [])
    )


def get_feed_between(start, end):
    key = "feed_range_{}_{}".format(start, end)
    resp = get_cached(
        key,
        "https://api.sibr.dev/eventually/v2/events?after={}&before={}&sortorder=asc&limit=100000".format(
            start, end
        ),
    )
    return resp


@unique
class EventType(IntEnum):
    # Can't use -1 because the Feed uses it for
    # "Undefined type; used in the Library for Leaders
    # and Postseason series matchups (plus currently-redacted messages)"
    NOT_YET_HANDLED_IN_ENUM = -99999
    # Pulled from https://www.blaseball.wiki/w/SIBR:Feed#Event_types
    LETS_GO = 0
    PLAY_BALL = 1
    HALF_INNING = 2
    PITCHER_CHANGE = 3
    STOLEN_BASE = 4
    WALK = 5
    STRIKEOUT = 6
    FLYOUT = 7
    GROUND_OUT = 8
    HOME_RUN = 9
    HIT_SINGLE_DOUBLE_TRIPLE = 10
    GAME_END_LOG = 11
    PLATE_APPEARANCE = 12
    STRIKE_NOT_INCLUDING_FOUL_BALLS = 13
    BALL = 14
    FOUL_BALL = 15
    HOME_FIELD_ADVANTAGE_ACTIVATION = 21
    HIT_BY_PITCH = 22
    PLAYER_SKIPPED_DUE_TO_BEING_SHELLED_FROZEN_OR_ELSEWHERE = 23
    PARTYING = 24
    STRIKE_ZAPPED_BY_ELECTRIC_BLOOD = 25
    MILD_PITCH = 27
    END_OF_INNING = 28
    BLACK_HOLE_COLLECT_10_IN_GAME = 30
    SUN_2_COLLECT_10_IN_GAME = 31
    BIRDS_CIRCLING_NO_SHELLED_PLAYER = 33
    BIRDS_FRIEND_OF_CROWS_PROC = 34
    COFFEE_3S_GAINING_TRIPLE_THREAT = 36
    COFFEE_2_GAINING_A_FREE_REFILL = 37
    COFFEE_GAINING_LOSING_WIRED_TIRED = 39
    FEEDBACK_SWAP = 41
    PEANUTS_ALLERGIC_REACTION = 47
    REVERB_ROSTER_SHUFFLE = 49
    BLOODDRAIN_SIPHON_PROC = 52
    SOLAR_ECLIPSE_INCINERATION = 54
    SOLAR_ECLIPSE_INCINERATION_BLOCKED_FIREPROOF_FIRE_EATER = 55
    FLOODING_BASERUNNERS_SWEPT = 62
    SALMON_INNING_BEGINS_AGAIN = 63
    ENTERING_THE_SECRET_BASE = 65
    EXITING_THE_SECRET_BASE = 66
    CONSUMERS_ATTACK_INCL_DEFENSE_WITH_ITEMS_YOLKED = 67
    ECHO_CHAMBER = 69  # nice
    GRIND_RAIL = 70
    PEANUT_MISTER = 72
    PEANUTS_FLAVOR_TEXT = 73
    TASTING_THE_INFINITE_SHELLING_VIA_HONEY_ROASTED = 74
    SOLAR_PANELS_START_UP_TEXT = 78
    RETURN_FROM_ELSEWHERE = 84
    OVER_UNDER = 85
    UNDER_OVER = 86
    UNDERSEA = 88
    HOMEBODY_HOMESICK_HAPPY_TO_BE_HOME = 91
    SUPERYUMMY_LOVES_MISSES_PEANUTS = 92
    PERK = 93
    SHAME_DONOR = 99
    ADDED_MODIFICATION_TRIPLE_THREAT_FREE_REFILL_MAGMATIC_INHABITING_ETC = 106
    REMOVED_MODIFICATION_SAME_AS_ABOVE_BUT_WHEN_THEY_DISAPPEAR = 107
    TIMED_MODIFICATION_EXPIRES = 108
    PLAYER_REMOVED_FROM_TEAM = 112
    PLAYER_TRADE = 113
    PLAYER_MOVE_RECRUIT_ETC = 115
    PLAYER_INCINERATION_REPLACEMENT = 116
    PLAYER_STAT_INCREASE = 117
    PLAYER_STAT_DECREASE = 118
    PLAYER_TEAM_ENTERS_THE_HALL_OF_FLAME = 125
    REVERB_SHUFFLE_ROTATION = 132
    PLAYER_HATCHED_REPLICA_CREATED = 137
    FINAL_STANDINGS = 143
    MODIFICATION_CHANGE_WIRED_TIRED_TRANSITIONS_REROLL_EGO_UPGRADE_ETC = 144
    ADDED_MODIFICATION_DUE_TO_ANOTHER_MOD_UNDER_OVER_PERK_PSYCHO_ACOUSTICS_ETC = 146
    REMOVED_MODIFICATION_ADDED_DUE_TO_ANOTHER_MOD_UNDER_OVER_PERK = 147
    CHANGED_MODIFIER_DUE_TO_ANOTHER_MODIFIER = 148
    TEAM_SHAMED_BY_ANOTHER = 154
    TEAM_SHAMES_ANOTHER = 155
    SUN_2_GRANTS_A_WIN_OUTCOME_PRE_S20 = 156
    BLACK_HOLE_SWALLOWS_A_WIN_OUTCOME_PRE_S20 = 157
    ELIMINATED_FROM_POSTSEASON = 158
    POSTSEASON_ADVANCE = 159
    HIGH_PRESSURE_THE_PRESSURE_IS_ON_OFF_OVERPERFORMING_ADDED_AND_REMOVED = 165
    ECHO_MESSAGE = 169
    SUPERPOSITION_ECHO_INTO_STATIC = 170
    REMOVED_MULTIPLE_MODIFICATIONS_ADDED_DUE_TO_ANOTHER_MOD_ECHO = 171
    ADDED_MULTIPLE_MODIFICATIONS_DUE_TO_ANOTHER_MOD_ECHO = 172
    PSYCHO_ACOUSTICS = 173
    RECEIVER_BECOMES_AN_ECHO = 174
    INVESTIGATION_PROGRESS_UPSHELLABLE_FOR_FISH = 175
    AMBITIOUS = 182

    # Ensure that not-yet-handled values warn us,
    # then default to a safe value
    @classmethod
    def _missing_(cls, value):
        print("!!! unknown type: {}".format(value))
        return cls.NOT_YET_HANDLED_IN_ENUM


@unique
class Weather(IntEnum):
    SUN_2 = 1
    ECLIPSE = 7
    GLITTER = 8
    BLOODDRAIN = 9
    PEANUTS = 10
    BIRDS = 11
    FEEDBACK = 12
    REVERB = 13
    BLACK_HOLE = 14
    COFFEE = 15
    COFFEE_2 = 16
    COFFEE_3S = 17
    FLOODING = 18
    SALMON = 19
    POLARITY_PLUS = 20
    POLARITY_MINUS = 21
    SUN_90 = 23
    SUN_POINT_1 = 24
    SUM_SUN = 25

    def is_coffee(self):
        return self.value in [
            self.COFFEE,
            self.COFFEE_2,
            self.COFFEE_3S,
        ]

    def is_polarity(self):
        return self.value in [
            self.POLARITY_PLUS,
            self.POLARITY_MINUS,
        ]

    def can_echo(self):
        return self.value in [
            self.FEEDBACK,
            self.REVERB,
        ]


@dataclass
class TeamData:
    data: Dict[str, Any]

    @property
    def id(self):
        return self.data["id"]

    @property
    def mods(self):
        return get_mods(self.data)

    def has_mod(self, mod) -> bool:
        return mod in self.mods


@dataclass
class StadiumData:
    data: Dict[str, Any]

    @property
    def id(self):
        return self.data["id"]

    @property
    def mods(self):
        return self.data["mods"]

    def has_mod(self, mod) -> bool:
        return mod in self.mods


null_stadium = StadiumData(
    {
        "id": None,
        "mods": [],
        "name": "Null Stadium",
        "nickname": "Null Stadium",
        "mysticism": 0.5,
        "viscosity": 0.5,
        "elongation": 0.5,
        "filthiness": 0,
        "obtuseness": 0.5,
        "forwardness": 0.5,
        "grandiosity": 0.5,
        "ominousness": 0.5,
        "fortification": 0.5,
        "inconvenience": 0.5,
        "hype": 0,
    }
)


@dataclass
class PlayerData:
    data: Dict[str, Any]

    @property
    def id(self):
        return self.data["id"]

    @property
    def mods(self):
        return get_mods(self.data)

    @property
    def name(self):
        unscattered_name = self.data.get("state", {}).get("unscatteredName")
        return unscattered_name or self.data["name"]

    @property
    def raw_name(self):
        return self.data["name"]

    def has_mod(self, mod) -> bool:
        return mod in self.mods

    def has_any(self, *mods) -> bool:
        for mod in mods:
            if mod in self.mods:
                return True
        return False

    def vibes(self, day):
        frequency = 6 + round(10 * self.data["buoyancy"])
        phase = math.pi * ((2 / frequency) * day + 0.5)

        pressurization = self.data["pressurization"]
        cinnamon = self.data["cinnamon"] if self.data["cinnamon"] is not None else 0
        viberange = 0.5 * (pressurization + cinnamon)
        vibes = (
            (viberange * math.sin(phase)) - (0.5 * pressurization) + (0.5 * cinnamon)
        )
        return vibes if not self.has_mod("SCATTERED") else 0


class GameData:
    def __init__(self):
        self.teams = {}
        self.players = {}
        self.stadiums = {}
        self.plays = {}
        self.games = {}
        self.sim = None

    def fetch_sim(self, timestamp, delta_secs: float = 0):
        timestamp = offset_timestamp(timestamp, delta_secs)
        key = "sim_at_{}".format(timestamp)
        resp = get_cached(
            key,
            "https://api.sibr.dev/chronicler/v2/entities?type=sim&at={}".format(
                timestamp
            ),
        )
        self.sim = resp["items"][0]["data"]

    def fetch_teams(self, timestamp, delta_secs: float = 0):
        timestamp = offset_timestamp(timestamp, delta_secs)
        key = "teams_at_{}".format(timestamp)
        resp = get_cached(
            key,
            "https://api.sibr.dev/chronicler/v2/entities?type=team&at={}&count=1000".format(
                timestamp
            ),
        )
        self.teams = {e["entityId"]: e["data"] for e in resp["items"]}

    def fetch_players(self, timestamp, delta_secs: float = 0):
        timestamp = offset_timestamp(timestamp, delta_secs)
        key = "players_at_{}".format(timestamp)
        resp = get_cached(
            key,
            "https://api.sibr.dev/chronicler/v2/entities?type=player&at={}&count=2000".format(
                timestamp
            ),
        )
        self.players = {e["entityId"]: e["data"] for e in resp["items"]}

    def fetch_stadiums(self, timestamp, delta_secs: float = 0):
        timestamp = offset_timestamp(timestamp, delta_secs)
        key = "stadiums_at_{}".format(timestamp)
        resp = get_cached(
            key,
            "https://api.sibr.dev/chronicler/v2/entities?type=stadium&at={}&count=1000".format(
                timestamp
            ),
        )
        self.stadiums = {e["entityId"]: e["data"] for e in resp["items"]}

    def fetch_player_after(self, player_id, timestamp):
        key = "player_{}_after_{}".format(player_id, timestamp)
        resp = get_cached(
            key,
            "https://api.sibr.dev/chronicler/v2/versions?type=player&id={}&after={}&count=1&order=asc".format(
                player_id, timestamp
            ),
        )
        for item in resp["items"]:
            self.players[item["entityId"]] = item["data"]

    def fetch_game(self, game_id):
        key = "game_updates_{}".format(game_id)
        resp = get_cached(
            key,
            "https://api.sibr.dev/chronicler/v1/games/updates?count=2000&game={}&started=true".format(
                game_id
            ),
        )
        self.games[game_id] = resp["data"]
        for update in resp["data"]:
            play = update["data"]["playCount"]
            self.plays[(game_id, play)] = update["data"]

    def fetch_league_data(self, timestamp, delta_secs: float = 0):
        self.fetch_sim(timestamp, delta_secs)
        self.fetch_teams(timestamp, delta_secs)
        self.fetch_players(timestamp, delta_secs)
        self.fetch_stadiums(timestamp, delta_secs)

    def get_update(self, game_id, play):
        if game_id not in self.games:
            self.fetch_game(game_id)
        update = self.plays.get((game_id, play))
        update["weather"] = Weather(update["weather"])
        return update

    def get_player(self, player_id) -> PlayerData:
        return PlayerData(self.players[player_id])

    def has_player(self, player_id) -> bool:
        return player_id in self.players

    def get_team(self, team_id) -> TeamData:
        return TeamData(self.teams[team_id])

    def get_stadium(self, stadium_id) -> StadiumData:
        return StadiumData(self.stadiums[stadium_id])
