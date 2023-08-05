Usage

  'instancemanager <project> <action>'

  or

  'instancemanger <action> <project>' 

  project -- The name of the project

  action -- The action to take, possible actions include:


    backup -- Backup the instance database.

    create -- Create a zope instance for your project.

    datafs -- Copy over a fresh, prepared, 'Data.fs'.

    fresh -- Wipe everything and create an instance including products.

    printconfig -- Print the configuration for this project.

    products -- Rebuild the Products/ directory .

    restart -- Restart the zope instance.

    restore -- Restore the last available backup of the database

    soft -- Restart zope and call the quickreinstall script.

    start -- Start the zope instance.

    stop -- Stop the zope instance.


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
  **instance manager** jumps in. 'instancemanager yourproject create'
  creates an instance in your default location. 'instancemanager
  yourproject fresh' gives you a freshly prepared products directory, a
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
  'instancemanager vanrees fresh'. And it updates a couple of other
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
