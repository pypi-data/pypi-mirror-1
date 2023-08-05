

Gazest
======



About
-----

Gazest is a community engine based around wiki-style information
editing.  What does that mean?  It's simply a wiki with some added
features to make it easy to have user interations outside of editing.



Installation
------------

You should be able to install Gazest using easy_install:

 $ easy_install gazest-X.Y.Z.tar.gz

Unfortunately, this won't work for most people.  To install Gazest the
hard way, do something like the following.  You will probably want to
setup a working env but this is optional:

 $ mkdir deploy
 $ cd deploy
 $ wget http://svn.colorstudy.com/home/ianb/workingenv/workingenv.py
 $ python workingenv.py wenv
 $ . wenv/bin/activate

Now install the deps that usually cause problems to `easy_install`:
 
 $ PYPI=http://pypi.python.org/packages/source
 $ wget $PYPI/S/SQLAlchemy/SQLAlchemy-0.3.11.tar.gz
 $ tar -zxvf SQLAlchemy-0.3.11.tar.gz
 $ cd SQLAlchemy-0.3.11
 $ python setup.py install
 $ cd ..

 $ svn co http://authkit.org/svn/AuthKit/tags/0.4.0/ authkit-0.4.0
 $ cd authkit-0.4.0
 $ python setup.py install
 $ cd ..

 $ wget $PYPI/P/Pylons/Pylons-0.9.6.1.tar.gz
 $ tar -zxvf Pylons-0.9.6.1.tar.gz
 $ cd Pylons-0.9.6.1
 $ python setup.py install
 $ cd ..

 $ wget http://effbot.org/downloads/Imaging-1.1.6.tar.gz
 $ tar -zxvf Imaging-1.1.6.tar.gz 
 $ cd Imaging-1.1.6
 $ python setup.py install
 $ cd ..

If running Python 2.4, you need `hashlib` and `uuid`.  You don't need
this with Python 2.5:

 $ easy_install hashlib
 $ easy_install uuid

You can now install Gazest:
 
 $ tar -zxvf gazest-X.Y.Z.tar.gz
 $ cd gazest-X.Y.Z
 $ python setup.py install
 $ cd ..

SQLite is not a requirement but if you plan to use it, now would be a
good time to install it:

 $ easy_install pysqlite



Setup
-----

Make a config file as follows:

 $ paster make-config gazest config.ini

Tweak the config file as appropriate and then setup the application:

 $ paster setup-app config.ini

Now visit your gazest site with a web browser and create a user.
You'll want to make this user your first thaumaturge.  In Gazest
parlance, thaumaturges are those who can cast evil away: they can ban
people.

Upgrade your new user:

 $ gazest-god-mode config.ini username



Hacking
-------

You can get the bleeding edge with `git`:

 $ git clone http://ygingras.net/files/gazest.git
 $ git clone http://ygingras.net/files/gazest_extra_macros.git
