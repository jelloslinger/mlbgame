#!/usr/bin/env python

"""Module that is used for getting information
about the (MLB) league and the teams in it.
"""

from __future__ import print_function

import mlbgame.data
import mlbgame.object

from datetime import datetime
import dateutil.parser
import lxml.etree as etree
import requests
import sys


def get_league_object():
    """Returns the xml object corresponding to the league

    Only designed for internal use"""
    # get data
    data = mlbgame.data.get_properties()
    # return league object
    return etree.parse(data).getroot().find('leagues').find('league')


def league_info():
    """Returns a dictionary of league information"""
    league = get_league_object()
    output = {}
    for x in league.attrib:
        output[x] = league.attrib[x]
    return output


def team_info():
    """Returns a list of team information dictionaries"""
    teams = get_league_object().find('teams').findall('team')
    output = []
    for team in teams:
        info = {}
        for x in team.attrib:
            info[x] = team.attrib[x]
        output.append(info)
    return output


class Info(mlbgame.object.Object):
    """Holds information about the league or teams

    Properties:
    club
    club_common_name
    club_common_url
    club_full_name
    club_id
    club_spanish_name
    dc_site
    display_code
    division
    es_track_code
    esp_common_name
    esp_common_url
    facebook
    facebook_es
    fanphotos_url
    fb_app_id
    field
    google_tag_manager
    googleplus_id
    historical_team_code
    id
    instagram
    instagram_id
    league
    location
    medianet_id
    mobile_es_url
    mobile_short_code
    mobile_url
    mobile_url_base
    name_display_long
    name_display_short
    newsletter_category_id
    newsletter_group_id
    photostore_url
    pinterest
    pinterest_verification
    pressbox_title
    pressbox_url
    primary
    primary_link
    secondary
    snapchat
    snapchat_es
    team_code
    team_id
    tertiary
    timezone
    track_code
    track_filter
    tumblr
    twitter
    twitter_es
    url_cache
    url_esp
    url_prod
    vine
    """

    def nice_output(self):
        """Return a string for printing"""
        return '{0} ({1})'.format(self.club_full_name, self.club.upper())

    def __str__(self):
        return self.nice_output()


class Roster(object):
    """Represents an MLB Team

    Properties:
        roster_url
        roster
        roster_json
        last_update
    """
    url = 'http://mlb.mlb.com/lookup/json/named.roster_40.bam?team_id=%s'

    def __init__(self, team_id=None):
        if team_id:
            self.roster_url = Roster.url % team_id
            self.roster = []
            self.parse_roster()
        else:
            try:
                raise NoTeamID('A `team_id` was not supplied.')
            except NoTeamID as e:
                print(e)
                raise

    @property
    def roster_json(self):
        """Return roster output as json"""
        try:
            return requests.get(self.roster_url).json()
        except requests.exceptions.RequestException as e:
            print(e)
            sys.exit(-1)

    @property
    def last_update(self):
        """Return a dateutil object from string [last update]
        originally in ISO 8601 format: YYYY-mm-ddTHH:MM:SS"""
        last_update = self.roster_json['roster_40']['queryResults']['created']
        return dateutil.parser.parse(last_update)

    def parse_roster(self):
        """Parse the json roster"""
        players = self.roster_json['roster_40']['queryResults']['row']
        for player in players:
            mlbplayer = Player(player)
            self.roster.append(mlbplayer)


class RosterException(Exception):
    """Roster Exceptions"""


class NoTeamID(RosterException):
    """A `team_id` was not supplied"""


class Player(mlbgame.object.Object):
    """Represents an MLB Player

    Properties:
        bats
        birth_date
        college
        end_date
        height_feet
        height_inches
        jersey_number
        name_display_first_last
        name_display_last_first
        name_first
        name_full
        name_last
        name_use
        player_id
        position_txt
        primary_position
        pro_debut_date
        start_date
        starter_sw
        status_code
        team_abbrev
        team_code
        team_id
        team_name
        throws
        weight
    """
    pass


class Standings(object):
    """Holds information about the league standings

    Properties:
        standings_url
        mlb_standings
        standings_json
        last_update
    """
    DIVISIONS = {
        'AL': {
            '201': 'AL East',
            '202': 'AL Central',
            '200': 'AL West',
        },
        'NL': {
            '204': 'NL East',
            '205': 'NL Central',
            '203': 'NL West',
        }
    }

    def __init__(self, date=datetime.now()):
        now = datetime.now()
        if date.year == now.year and date.month == now.month and date.day == now.day:
            self.standings_url = ('http://mlb.mlb.com/lookup/json/named.standings_schedule_date.bam?season=%s&'
                                    'schedule_game_date.game_date=%%27%s%%27&sit_code=%%27h0%%27&league_id=103&'
                                    'league_id=104&all_star_sw=%%27N%%27&version=2') % (date.year, date.strftime('%Y/%m/%d'))
            self.standings_schedule_date = 'standings_schedule_date'
        else:
            self.standings_url = ('http://mlb.mlb.com/lookup/json/named.historical_standings_schedule_date.bam?season=%s&'
                                    'game_date=%%27%s%%27&sit_code=%%27h0%%27&league_id=103&'
                                    'league_id=104&all_star_sw=%%27N%%27&version=48') % (date.year, date.strftime('%Y/%m/%d'))
            self.standings_schedule_date = 'historical_standings_schedule_date'
        self.mlb_standings = []
        self.parse_standings()

    @property
    def standings_json(self):
        """Return standings output as json"""
        try:
            return requests.get(self.standings_url).json()
        except requests.exceptions.RequestException as e:
            print(e)
            sys.exit(-1)

    @property
    def divisions(self):
        """Return an array of Divison objects"""
        return self.mlb_standings

    @property
    def last_update(self):
        """Return a dateutil object from string [last update]
        originally in ISO 8601 format: YYYY-mm-ddTHH:MM:SS"""
        last_update = self.standings_json[self.standings_schedule_date]['standings_all_date_rptr']['standings_all_date'][0]['queryResults']['created']
        return dateutil.parser.parse(last_update)

    def parse_standings(self):
        """Parse the json standings"""
        sjson = self.standings_json[self.standings_schedule_date]['standings_all_date_rptr']['standings_all_date']
        for league in sjson:
            if league['league_id'] == '103':
                divisions = Standings.DIVISIONS['AL']
            elif league['league_id'] == '104':
                divisions = Standings.DIVISIONS['NL']
            else:
                # Raise Error
                try:
                    raise UnknownLeagueID('An unknown `league_id` was passed from standings json.')
                except UnknownLeagueID as e:
                    print('StandingsError: %s' % e)
                    raise
                    sys.exit(-1)

            for division in divisions:
                mlbdivision = []
                mlbdiv = type('Division', (object,), {'name': divisions[division]})
                teams = [team for team in league['queryResults']['row'] if team['division_id'] == division]
                for team in teams:
                    mlbteam = type('Team', (object,), team)
                    mlbdivision.append(mlbteam)
                setattr(mlbdiv, 'standings', mlbdivision)
                self.mlb_standings.append(mlbdiv)


class StandingsException(Exception):
    """Standings Exceptions"""


class UnknownLeagueID(StandingsException):
    """An unknown `league_id` was passed from standings json"""


# class Division(object):
#     """Represents an MLB Division in the standings

#     Properties:
#         name
#         teams
#     """

# class Team(object):
#     """Represents an MLB team in the standings

#     Properties:
#         streak
#         playoff_odds
#         elim
#         x_wl_seas
#         vs_right
#         gb
#         sit_code
#         home
#         last_ten
#         one_run
#         vs_division
#         playoff_points_sw
#         vs_left
#         is_wildcard_sw
#         vs_west
#         away
#         division_champ
#         pct
#         team_short
#         clinched_sw
#         playoffs_sw
#         playoffs_flag_mlb
#         division_id
#         division
#         interleague
#         playoffs_flag_milb
#         opp_runs
#         wild_card
#         elim_wildcard
#         x_wl
#         file_code
#         team_full
#         runs
#         wildcard_odds
#         vs_east
#         l
#         gb_wildcard
#         team_abbrev
#         points
#         place
#         w
#         division_odds
#         team_id
#         vs_central
#         extra_inn
#     """


class Injuries(object):
    """Represents the MLB Disabled List

    Properties:
        injury_url
        injuries
        team_id
        injury_json
        last_update
    """
    injury_url = 'http://mlb.mlb.com/fantasylookup/json/named.wsfb_news_injury.bam'

    def __init__(self, team_id=None):
        if team_id:
            self.injury_url = Injuries.injury_url
            self.injuries = []
            if isinstance(team_id, int):
                self.team_id = str(team_id)
            else:
                try:
                    raise TeamIDException('A `team_id` must be an integer.')
                except TeamIDException as e:
                    print(e)
                    raise
            self.parse_injury()
        else:
            try:
                raise TeamIDException('A `team_id` was not supplied.')
            except TeamIDException as e:
                print(e)
                raise

    @property
    def injury_json(self):
        """Return injury output as json"""
        try:
            return requests.get(self.injury_url).json()
        except requests.exceptions.RequestException as e:
            print(e)
            sys.exit(-1)

    @property
    def last_update(self):
        """Return a dateutil object from string [last update]
        originally in ISO 8601 format: YYYY-mm-ddTHH:MM:SS"""
        last_update = self.injury_json['wsfb_news_injury']['queryResults']['created']
        return dateutil.parser.parse(last_update)

    def parse_injury(self):
        """Parse the json injury"""
        injuries = self.injury_json['wsfb_news_injury']['queryResults']['row']
        injuries = [injury for injury in injuries if injury['team_id'] == self.team_id]
        for injury in injuries:
            mlbinjury = Injury(injury)
            self.injuries.append(mlbinjury)


class injuryException(Exception):
    """injury Exceptions"""


class TeamIDException(injuryException):
    """A `team_id` was not supplied or the `team_id` was not an integer."""


class Injury(mlbgame.object.Object):
    """Represents an MLB injury

    Properties:
        display_ts
        due_back
        injury_desc
        injury_status
        injury_update
        insert_ts
        league_id
        name_first
        name_last
        player_id
        position
        team_id
        team_name
    """
    pass
