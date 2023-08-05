Usage

    usage: Usage: instancemanager [options] [multi-action] <project>
    multi-action: default ones are 'fresh' and 'soft'.
    project: the name of the project, available projects are:
        <project>
        etc.

        You can use ALL to perform the action for all projects.

    options:
      -h, --help           show this help message and exit
      -v, --verbose        Show all logging messages.
      -q, --quiet          Only show error messages.
      -m, --manifest       Print Manifest of installed Products and collisions (with --products)
      -b, --backup         Backup the instance database (incremental backup).
      --changeown          Action that changes ownership of some documents.
      --copydatafs         Copy over a fresh, prepared, 'Data.fs'.
      --create             Create a zope instance for your project.
      --pack               Action that packs your database.
      --printconfig        Print the configuration for this project.
      --products           Rebuild the Products/ directory .
      -r, --reinstall      Action that quickreinstalls your products.
      --repozo=REPOZO      Other backup/restore tasks with repozo.
      --restore            Restore the database from the regular backup.
      --restore-date=DATE  Restore situation at DATE from regular backup.
      -tPRD, --test=PRD    Runs tests for product PRD (use ALL for all products).
      --zeo=CMD            Runs your zeo server's 'bin/zeoctl CMD'.
      -zCMD, --zope=CMD    Runs your instance's 'bin/zopectl CMD'.

Quick intro
  
  * Install as described in INSTALL.txt
  
  * Run instancemanager once to create a .instancemanager directory in ~
  
  * Edit userdefaults.py in ~ for only the common basis for all your sites 
    (example, Zope path, default admin and password for new sites)
  
  * Copy userdefaults.py in ~ to <project>.py (typically "customer.com.py")
    and customize (override) for that project (port, plone site name, products, etc.)
  
  * Now this will do the full setup for your site. ONLY do it when you want a TOTALLY fresh start::
  
      instancemanager fresh <project>    # NOT <project>.py - 

  * to stop zope::
  
      instancemanager -z stop <project> 
  
  * to start in foreground::
  
      instancemanager -z stop <project> 
    
  * to reinstall products::
  
      instancemanager --products <project> 
      
    or::
    
      instancemanager --products --manifest <project>   # to get a (wide) manifest
         # that can help diagnose product version issues and collisions from bundles 
  
  More details below.
    
Details

  Setting up a zope instance, symlinking to all the products, extracting
  product tarballs, copying over a snapshot Data.fs from the customer's
  website, restarting zope, clicking around in the quickinstaller: *it
  can all be done by hand*.

  Instancemanager is a handy utility program that manages your
  development zope instances:

  * Creates clean, fresh instances in your standard location.

  * Copies over a prepared Data.fs if desired.

  * Makes products available in the 'Products/' directory from a variety
    of sources (.tgz, .tgz bundles, svn, symlinking).

  * Restarts your zope and reinstalls your products.

  * Does the Data.fs copy, the product availability and the reinstall in
    one step, giving you a real fresh instance without leftover junk.

  * Make backups and restores of the instance database to a directory. By default
    backups are stored in ~/backups/<project> which will be created if it doesn't
    exist.

  If you're the kind of good developers that's also a lazy developer,
  you don't want to do this repetitive stuff by hand. That's where the
  **instance manager** jumps in. 'instancemanager  --create yourproject'
  creates an instance in your default location. 'instancemanager
  fresh yourproject ' gives you a freshly prepared products directory, a
  freshly copied pre-made Data.fs (if you've got one) and it presses the
  quickinstaller buttons you want pressed.

  For instance, individual product sources can be:

  * A '.tgz' file (like FCKeditor or qGoogleSitemaps).

  * A '.tgz' bundle (like plone or ploneformmailer).

  * A symlink (most probably to an svn directory, for instance your
    current customer development product).

  * A symlink to a bundle directory (most probably an svn bundle, for
    instance the latest plone 2.5).

  Configuration is handled in a layered manner. Instancemanager has its
  own defaults. You can overwrite these global defaults locally ("I
  always store my instances in my homedir instead of '~/instances/'").
  And there's an per-project config file where you can list
  exceptions. And of course the passwords and desired products and so.

  If you specify the ID of your plone root ('plone_site_name'), the
  instancemanager attempts a quick-reinstall of your products when
  running the "fresh" or "soft" targets. Real handy during
  development. It even migrates plone to a newer version when
  needed. I'm able to migrate http://vanrees.org/ from a plone 2.1
  website to plone 2.5, including migration, with just a call to
  'instancemanager fresh vanrees '. And it updates a couple of other
  products too, while it's at it. This removes the need for much by-hand
  action when testing migrations or when doing installer updates on your
  product.

  When you have specified a plone_site_name and a PloneSite of that name
  does not exist yet, instancemanager tries to create that.  Works for
  plone 2.1 and 2.5.  It has some oddities still though.  When the
  script has run for the first time, a 'bin/zopectl status' cannot find
  the zope process, though it *is* running.  Shutting it down via the
  Control Panel and then restarting it from the command line seems the
  best option here.  Some testing is needed to improve this.  Upon
  trying again after minor changes it seems to work fine actually.
  Still: consider this experimental, so: start experimenting. :)
