=======
mlbgame
=======

mlbgame is a Python API to retrieve and read MLB GameDay XML data.
mlbgame works with real time data, getting information as games are being played.

mlbgame uses the same data that MLB GameDay uses,
and therefore is updated as soon as something happens in a game.

mlbgame currently comes pre-loaded with every game
from 2012 to the end of the 2015 season,
but will be updated regularly during the season.
Therefore, accessing this data does not actually make a request to mlb.com

mlbgame `documentation <http://zachpanz88.github.io/mlbgame>`__

mlbgame on `Github <https://github.com/zachpanz88/mlbgame>`__  (Source Code)

If you have a question or need help, the quickest way to get a response 
is to file an issue on the `Github issue tracker <https://github.com/zachpanz88/mlbgame/issues/new>`__

mlbgame's submodules (except for ``statmap``) should not really be used other than as 
used by the main functions of the package (in ``__init__.py``).

Updating the Game Database
--------------------------

Since games happen every day, new game data exists that is not stored on disk from the original install.
The database can be updated by running the following command:

::

    mlbgame-update

There are some optional arguments that will cache extra data that is not included with the original install.
This extra data may take up a lot of disk space, so only cache if you really need it (it will make processes much faster).
If this data is not cached, mlbgame will make a request to mlb.com every time you try to access the data.

::

    usage: mlbgame-update <arguments>
    
    Arguments:
    --help (-h)                     display this help menu
    --hide                          hides output from update script
    --more (-m)                     saves the box scores and individual game stats from every game
    --start (-s) <MM-DD-YYYY>       date to start updating from (runs until current day) (default: 01-01-2012)

Use of mlbgame must follow the terms stated in the 
`license <https://raw.githubusercontent.com/zachpanz88/mlbgame/master/LICENSE>`__ 
and on `mlb.com <http://gd2.mlb.com/components/copyright.txt>`__