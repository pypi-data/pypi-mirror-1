# Release information about tgmigrate

version = "0.1"

description = "sqlalchemy migrate command"
long_description = """tgmigrate is an turbogears command extension which provide sqlalchemy migrate support.
http://erosson.com/migrate/
The first version of tgmigrate gives turbogears developers a quick evaluation if sqlalchemy migrate is helpful for us.


Install
----------------
easy_install tgmigrate


Usage
----------------

After install, tgmigrate plug an "migrate" command into tg-admin console utility.

The basic syntax is ::

    tg-admin migrate [command]

tgmigrate takes care the dburi and repository name for you.

The reference procedure is:

1. quickstart project as usual::
    
    $ tg-admin quickstart -i -s demo
    
2. setup sqlalchemy dburi in demo/dev.cfg

3. create initial database

    $ tg-admin sql create
    
4. create repository "migration" 

    $ tg-admin migrate create
    
note the default repository folder named "migration" is created in your project folder.

5. move your database to version control

    $ tg-admin migrate version_control
    
or briefly:
    
    $ tg-admin migrate vc
    
6. Now you could watch the current version in both database and repository

show repository version::

    $ tg-admin migrate v 
    (tg-admin migrate version)

show database version::
    
    $ tg-admin migrate dbv 
    (tg-admin migrate db_version)
    
then follow the migration doc http://erosson.com/migrate/docs/versioning.html to do the further stuff.

I must confess that at this time I havn't go through the further stuff in the doc, so if you found sqlalchemy migrate is helpful, 
please let me know. (say something back to TurboGears google group http://groups.google.com/group/turbogears)


reference
--------------
Available commands are

$ tg-admin migrate [command]

command = [
'help',
'create',
'script',
'commit',
'version',
'source',
'version_control',
'db_version',
'upgrade',
'downgrade',
'drop_version_control',
'manage',
'test']


Caution
------------
It's an evaluation build, the project propose is giving turbogears developers a quick evaluation for sqlalchemy migrate function,
It's no harm for you, but no further support guaranteed.

""" 
author = "Fred Lin"
email = "gasolin+tg@gmail.com"
copyright = "Fred Lin 2006"

# if it's open source, you might want to specify these
url = "docs.turbogears.org"
download_url = "http://www.python.org/pypi/tgmigrate/"
license = "MIT"
