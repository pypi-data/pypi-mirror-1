whatsup
=======

whatsup is an outage escalation tool for a list of sites and contacts


Installing whatsup
------------------

whatsup is installable via ``easy_install`` or ``python setup.py`` in
the usual way from the python source at https://svn.openplans.org/svn/whatsup.  The recommended installation procedure is with
``virtualenv``::

     python <(curl http://svn.colorstudy.com/virtualenv/trunk/virtualenv.py) whatsup
     cd whatsup
     . bin/activate
     mkdir src
     cd src
     svn co https://svn.openplans.org/svn/whatsup
     cd whatsup
     python setup.py develop

You will also need data files (.ini) for contacts and sites.  By
default these live in ``${VIRTUAL_ENV}/src/whatsup/contacts`` and
${VIRTUAL_ENV}/src/whatsup/sites, though this is configurable.


Instantiating whatsup
---------------------

whatsup is served by the paste .ini file::

    paster serve whatsup.ini

Application options may be specified in this .ini file in the
``[app:whatsup]`` section prefixed with ``whatsup.``:

 * contacts, sites: location of the contacts and sites files.  can be
   a single file or a directory containing .ini files

 * auto_reload: whether to reload the configuration on each request

 * ping: whether to ping the sites
 
 * ping_frequency:  how often, in seconds, to ping the sites

 * smtp_from: who to send email as if the user does not specified

 * smtp_server: mail server to use.  If not specified, whatsup will
   not send email



whatsup contact .ini files
--------------------------

A contact .ini file contains one or more sections, each corresponding
to a contact.  The name of the section should be the name of the
contact.  Several data are specifiable for each contact:

 * email: comma separated list of email addresses.

 * phone: comma separated list of phone numbers

 * irc: comma separated list of IRC names

 * aim: AIM screenname

 * url: canonical web presence

 * contact: description of how to contact this person, or a filename
   containing that information

For each comma separated list, the first item is considered primary.


whatsup site .ini files
-----------------------

A site .ini file contains one or more sections, each corresponding to
a website.  By convention, the section name is the domain name of the
site.  Several data are specifiable for each site:

 * url: location of the site.  If not specified, the url will be from
   the section name (presumedly the domain name)

 * contact: comma separated list of contacts in case of site outage

 * description: brief description of the website

 * outage_procedure: if specified, a description of what to do in case
   the site is down or a filename containing that information.  By
   default, this links to the contact form which emails the contacts
   upon submission.

 * trac: URL of the associated Trac site
