== Installation ==

    sudo python setup.py install

== Usage (New Project) ==

    Create a project:
        squash create <project-name>
    
    Open a new ticket:
        squash open "This is the short description"

    Serve the project:
        squash serve
    
    Open in your browser, have fun.

== Usage (Existing Project) ==

    Clone the project:
        squash clone <project-url>

    List outstanding tickets:
        squash list --outstanding

    Close an existing ticket:
        squash close 8115
    
    Edit a ticket's YAML with an editor:
        squash edit 8115

    Update the project (in case something changed):
        squash pull

    Push back up:
        squash push

== Development Installation ==

A quick way to get going on Squash locally:
    - Download/Checkout Django into a django folder into the root of the repository:
         svn co http://code.djangoproject.com/svn/django/trunk/django django
    - Download/Clone Green Tea into the javascript folder:
         hg clone http://bitbucket.org/DeadWisdom/green-tea/ squash/js/tea/
    - Go into the squash Django project:
         cd squash
    - Add a settings_local.py, and tell Django to serve static files:
         echo "SERVE_STATIC = True" > settings_local.py
    - Initialize the Database, it will ask you to create a superuser, do so.
         ./manage.py syncdb
    - Run the server:
         ./manage.py runserver
    - Connect via a web-browser:
         http://localhost:8000/
    - Run the tests:
         http://localhost:8000/#test

By default, it will use SQLite as the dbms, storing to a "sqlite.db" file. The
best place to alter this is in the "settings_local.py" file, following the
Django Settings instructions: http://docs.djangoproject.com/en/dev/topics/settings/

== Green Tea ==
Squash is now based on a new javascript UI library called "Green Tea". Green
Tea is being jointly developed with Squash, so it must be manually inserted
into any clone.

To get it going, clone Green Tea, and put it in the squash/js/ folder as
squash/js/tea/:

    hg clone http://bitbucket.org/DeadWisdom/green-tea/ squash/js/tea/

== Tests ==
Tests are executed by going to #test in the root, so like: http://localhost:8000/#test
