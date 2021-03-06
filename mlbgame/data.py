#!/usr/bin/env python

"""This module gets the XML data that other functions use.
It checks if the data is cached first, and if not,
gets the data from mlb.com.
"""

import os

try:
    from urllib.request import urlopen
    from urllib.error import HTTPError
except ImportError:
    from urllib2 import urlopen, HTTPError


# Templates For URLS
BASE_URL = ('http://gd2.mlb.com/components/game/mlb/'
            'year_{0}/month_{1:02d}/day_{2:02d}/')
GAME_URL = BASE_URL + '/gid_{3}/{4}'
PROPERTY_URL = 'http://mlb.mlb.com/properties/mlb_properties.xml'
# Local Directory
PWD = os.path.join(os.path.dirname(__file__))


def get_scoreboard(year, month, day):
    """Return the game file for a certain day matching certain criteria."""
    try:
        data = urlopen(BASE_URL.format(year, month, day
                                       ) + 'scoreboard.xml')
    except HTTPError:
        data = os.path.join(PWD, 'default.xml')
    return data


def get_box_score(game_id):
    """Return the box score file of a game with matching id."""
    year, month, day = get_date_from_game_id(game_id)
    try:
        return urlopen(GAME_URL.format(year, month, day,
                                       game_id,
                                       'boxscore.xml'))
    except HTTPError:
        raise ValueError("Could not find a game with that id.")


def get_game_events(game_id):
    """Return the game events file of a game with matching id."""
    year, month, day = get_date_from_game_id(game_id)
    try:
        return urlopen(GAME_URL.format(year, month, day,
                                       game_id,
                                       'game_events.xml'))
    except HTTPError:
        raise ValueError("Could not find a game with that id.")


def get_overview(game_id):
    """Return the linescore file of a game with matching id."""
    year, month, day = get_date_from_game_id(game_id)
    try:
        return urlopen(GAME_URL.format(year, month, day,
                                       game_id,
                                       'linescore.xml'))
    except HTTPError:
        raise ValueError("Could not find a game with that id.")


def get_players(game_id):
    """Return the players file of a game with matching id."""
    year, month, day = get_date_from_game_id(game_id)
    try:
        print(GAME_URL.format(year, month, day, game_id, "players.xml"))
        return urlopen(GAME_URL.format(year, month, day,
                                       game_id,
                                       "players.xml"))
    except HTTPError:
        raise ValueError("Could not find a game with that id.")


def get_properties():
    """Return the current mlb properties file"""
    try:
        return urlopen(PROPERTY_URL)
    # in case mlb.com depricates this functionality
    except HTTPError:
        raise ValueError('Could not find the properties file. '
                         'mlb.com does not provide the file that '
                         'mlbgame needs to perform this operation.')


def get_date_from_game_id(game_id):
    year, month, day, _discard = game_id.split('_', 3)
    return int(year), int(month), int(day)
