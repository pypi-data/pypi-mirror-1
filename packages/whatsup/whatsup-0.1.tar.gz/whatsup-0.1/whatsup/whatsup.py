"""
whatsup: a view with webob
"""

import datetime
import os
import smtplib
import urllib
import urllib2

from genshi.builder import Markup
from genshi.template import TemplateLoader
from martini.config import ConfigMunger
from martini.utils import getbool
from martini.utils import getlist
from paste.urlparser import StaticURLParser
from pkg_resources import resource_filename
from webob import Request, Response, exc

class WhatsupView(object):

    ### class level variables
    defaults = { 'auto_reload': 'False',
                 'contacts': None,
                 'sites': None,
                 'ping': True,
                 'ping_frequency': 30, # seconds

                 # variables for email
                 'smtp_from': 'whatsup@localhost',
                 'smtp_server': None,
                 'smtp_port': 25,
                 'smtp_user': None,
                 'smtp_password': None
                 }

    def __init__(self, **kw):

        # set defaults
        for key in self.defaults:
            setattr(self, key, kw.get(key, self.defaults[key]))
        self.auto_reload = getbool(self.auto_reload)
        self.ping = getbool(self.ping)
        self.static = resource_filename(__name__, 'static')
        self.fileserver = StaticURLParser(self.static)

        # ensure data files exist
        assert os.path.exists(self.sites)
        assert os.path.exists(self.contacts)

        # response functions
        self.response_functions = { 'GET': self.get,
                                    'POST': self.post,
                                    }

        # template loader
        templates_dir = resource_filename(__name__, 'templates')
        self.loader = TemplateLoader(templates_dir,
                                     auto_reload=self.auto_reload)

        # status of sites
        self.status = {}
        self.errors = {}
        if self.ping:
            self.ping_frequency = datetime.timedelta(seconds=int(self.ping_frequency))            
            self.ping_sites(self.sites_data())
        

    ### methods dealing with HTTP

    def __call__(self, environ, start_response):
        request = Request(environ)
        if request.path_info.strip('/'):
            f = os.path.join(self.static, request.path_info.strip('/'))
            if os.path.exists(f):
                return self.fileserver(environ, start_response)
        res = self.make_response(request)
        res.delete_cookie('message')
        return res(environ, start_response)
                                
    def make_response(self, request):
        return self.response_functions.get(request.method, self.error)(request)

    def get_response(self, text, content_type='text/html'):
        res = Response(content_type=content_type, body=text)
        return res

    def get(self, request):
        """
        return response to a GET requst
        """

        path = request.path_info.strip('/')

        # template data dictionary      
        data = { 'contacts': self.contact_data(),
                 'sites': self.sites_data(),
                 }

        if 'message' in request.cookies:
            data['message'] = urllib.unquote(request.cookies['message'])
        else:
            data['message'] = None

        # site status
        data['status'] = self.status
        data['errors'] = self.errors
        if self.ping:
            now = datetime.datetime.now()
            if now - self.last_ping > self.ping_frequency:
                self.ping_sites(data['sites'])
        
        # render the template
        if path == 'contacts':
            template = 'contacts.html'
        elif path == 'contact' or path.startswith('contact/'):
            if path.startswith('contact/'):
                name = path.split('contact/', 1)[-1]
                name = ' '.join(name.split('+'))
            else:
                name = request.params.get('name')
            if name in data['contacts']:
                data['name'] = name
                template = 'contact.html'
            else:
                raise exc.HTTPTemporaryRedirect(location='/contacts')
        elif path == 'outage':
            site = request.params.get('site')
            template = 'outage.html'
            data['site'] = site
        elif path == 'fixed':
            site = request.params.get('site')
            if not self.status.get(site, {}).get('down', False):
                redirect = exc.HTTPSeeOther(location="/")
                message = site and ("%s is reported up" % site) or "Site not provided"
                redirect.set_cookie('message', urllib.quote(message))

                raise redirect
            template = 'fixed.html'
            data['site'] = request.params.get('site')
        else:
            template = 'index.html'
        template = self.loader.load(template)
        res = template.generate(**data).render('html', doctype='html')

        # return the response
        return self.get_response(res)

    def post(self, request):
        """
        return response to a POST request
        """
        path = request.path_info.strip('/')
        message = None
        if path == 'outage':
            site = request.params['site']
            problem = request.params['problem']
            email = request.params['email'] or self.smtp_from
            notify = request.params.get('notify')
            self.report_error(site, problem)
            if notify:
                self.status[site]['contact'].add(email)
            email = self.contact_site(site, problem, email)
            message = 'The outage of %s has been reported to %s' % (site, ', '.join(email))
        if path == 'fixed':
            site = request.params['site']
            fix = request.params['fix']
            email = request.params['email'] or self.smtp_from
            contacts = self.status[site].get('contact', [])
            self.status[site] = { 'down': False, 
                                  'date': datetime.datetime.now(),
                                  'message': fix }
            self.send_email(email, contacts, fix, Subject='%s reported up' % site)
            message = 'The outage of %s has been reported fixed' % site

        redirect = exc.HTTPSeeOther(location="/")
        if message:
            redirect.set_cookie('message', urllib.quote(message))
        raise redirect

    def error(self, request):
        """deal with non-supported methods"""
        return exc.HTTPMethodNotAllowed("Only %r operations are allowed" % self.response_functions.keys())
        
    ### internal methods
    
    def configuration(self, path):
        if os.path.isdir(path):
            files = [ os.path.join(path, f) for f in os.listdir(path) 
                      if f[-4:] == '.ini' ]
        else:
            files = [ path ]
        return ConfigMunger(*files).dict()


    def sites_data(self):
        if hasattr(self, '_sites'):
            return self._sites

        sites = self.configuration(self.sites)
        for name, site in sites.items():
            if not site.has_key('url'):
                site['url'] = 'http://' + name
            
            # site contacts
            site['contact'] = getlist(site.get('contact', ''))
            
            # additional email addresses to send to on site failure
            site['email'] = getlist(site.get('email', ''))

            # outage escalation procedure
            outage_procedure = site.get('outage_procedure')
            if outage_procedure:
                if os.path.isabs(outage_procedure):
                    filename = outage_procedure
                else:
                    filename = os.path.join(self.sites, outage_procedure)
                if os.path.exists(filename):
                    outage_procedure = file(filename).read()
                site['outage_procedure'] = Markup(outage_procedure)

        if not self.auto_reload:
            self._sites = sites

        return sites
            

    def contact_data(self):
        if hasattr(self, '_contacts'):
            return self._contacts
        contacts = self.configuration(self.contacts)
        
        for name, contact in contacts.items():
            contact['email'] = getlist(contact.get('email', ''))
            contact['phone'] = getlist(contact.get('phone', ''))
            prefered = contact.get('contact')
            if prefered is not None and prefered not in contact:
                if os.path.isabs(prefered):
                    filename = prefered
                else:
                    filename = os.path.join(self.contacts, prefered)
                if os.path.exists(filename):
                    contact['contact'] = file(filename).read()
                contact['contact'] = Markup(contact['contact'])

        if not self.auto_reload:
            self._contacts = contacts

        return contacts

    def report_error(self, site, error):
        now = datetime.datetime.now()
        site_status = self.status.setdefault(site, {})
        if site_status.get('down', False) == False:
            site_status['down'] = True
            site_status['date'] = now
            site_status['contact'] = self.contact_emails(site)
        self.errors.setdefault(site, []).append((now, error))
            
    def ping_sites(self, sites):
        now = datetime.datetime.now()
        for name, site in sites.items():
            if 'url' in site:
                try:
                    urllib2.urlopen(site['url'])
                    self.status.setdefault(name, {})['down'] = False
                    self.status.pop('message', None)
                    self.status[name]['date'] = now
                except urllib2.URLError, e:
                    message = '%s : %s' % (e.code, e.msg)
                    self.report_error(name, message)
            else:
                self.status.setdefault(name, {})['down'] = None
        self.last_ping = now

    def contact_emails(self, site):
        site = self.sites_data()[site]
        contacts = self.contact_data()
        email = site['email'][:]
        for contact in site['contact']:
            contact = contacts[contact]
            if contact['email']:
                email.append(contact['email'][0])
        return set(email)

    def contact_site(self, name, message, from_addr=None):
        # XXX only contact by email for now
        site = self.sites_data()[name]
        contacts = self.contact_data()
        email = self.contact_emails(name)
        if email and self.smtp_server:
            self.send_email(from_addr, email, message, Subject='%s site outage' % name)
        return email

    def send_email(self, from_addr, recipients, message, **headers):
        # ensure list of recipients
        if isinstance(recipients, basestring):
            recipients = [ recipients ]
        recipients = list(recipients)

        headers['To'] = ', '.join(recipients)
        headers['From'] = from_addr 
        headers['Content-Type'] = 'text/plain'
        message = '\n'.join('%s: %s' % (header, value) 
                            for header, value in headers.items()) + '\n\n' + message

        # send the email
        session = smtplib.SMTP(self.smtp_server, self.smtp_port)
        if self.smtp_user: # authenticate
            session.login(self.smtp_user.encode('utf-8'),
                          self.smtp_password.encode('utf-8'))
        session.sendmail(from_addr, recipients, message)

