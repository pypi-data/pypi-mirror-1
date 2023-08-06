defaultencodinghack
===================

Sets default encoding to utf8 in a hacky manner. While this is `considered
harmful <http://faassen.n--tree.net/blog/view/weblog/2005/08/02/0>`_, it is
sometimes necessary.

Encouraging pysqlite, SQLAlchemy and Archetypes to play together
----------------------------------------------------------------

In your buildout.cfg::

    [versions]
    pysqlite = 2.4.1

    [instance]
    eggs +=
        defaultencodinghack
    zcml +=
        defaultencodinghack
