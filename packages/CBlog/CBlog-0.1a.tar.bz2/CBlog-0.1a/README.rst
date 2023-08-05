CBlog
=====

CBlog is a simple weblog application based on the TurboGears_ framework.

Apart from being used by myself as the software that drives my personal blog,
it is also a useful showcase for various TG programming patterns.

The software is currently in alpha state, because the data model and the API
(internal and external, i.e. URls) may still change frequently and some
features I consider important are still missing. That being said, I already use
it on a regular basis for my own blog site.

.. _TurboGears: http://turbogears.org


Please see the 'doc' subdirectory for some more (sparse) information.

Quickstart in 10 steps:

    1.  Unpack distribution.
    2.  Open a terminal and change into the ``CBlog-0.1a`` directory.
    3.  Run ``tg-admin sql create``.
    4.  Run ``sqlite3 data/devdata.sqlite <data/bootstrap.sql``.
    5.  Development mode:

        Run ``./run dev.cfg``

        Production mode:

        1. First time only: ``cp data/devdata.sqlite data/proddata.sqlite``
        2. Run ``./run``

    6.  Open browser at ``http://localhost:8080/`` (developmentmode)
        resp. at ``http://localhost:8081/`` (production mode).
    7.  Log in with username/password ``admin`` and then click on
        *Administration*.
    8.  Add a user and add him to the *Blog publishers* group.
    9.  Log out as admin and log-in again as the new user.
    10. Start adding blog articles!

Share and Enjoy!
