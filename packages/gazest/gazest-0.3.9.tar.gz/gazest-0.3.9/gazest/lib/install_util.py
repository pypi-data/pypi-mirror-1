
from paste.script.appinstall import Installer
from mako.template import Template
from paste.script import copydir
from paste.script.command import NoDefault
from pprint import pprint
from os.path import dirname

from paste.deploy.converters import asbool
from gazest.lib.request_util import parse_timedelta

class IniOpt:
    def __init__(self, key, default=NoDefault, prompt=True):
        """
        `key`: the keyword sent to Mako
        
        `default`: offered as default; if NoDefault, the user must
        supply a value; if boolean, the value will be coerced to bool;
        if callable, it will be called at runtime to get the default,
        it will receive the dict of values known so far.

        `prompt`: how to prompt the user; if True, the key name is
        used to prompt; if False, the default is accepted without
        prompting the user; if callable, called with the dict of known
        values; otherwise, uses as-is to prompt the user.
        """
        self.key = key
        self.default = default
        self.prompt = prompt

    def request(self, vars, command):
        default = self.default
        if callable(default) and default is not NoDefault:
            default = self.default(vars)

        if isinstance(self.default, bool):
            prompt_f = command.ask
        else:
            prompt_f = command.challenge

        if callable(self.prompt):
            prompt = self.prompt(vars)
        elif self.prompt is True:
            prompt = self.key.replace("_", " ")
        else:
            prompt = self.prompt
            
        if self.key not in vars:
            if command.interactive and prompt:
                vars[self.key] = prompt_f(prompt, default=default)
            elif default is not NoDefault:
                vars[self.key] = default
            else:
                msg = "Can't generate configuration: '%s' missing" % self.key
                raise Exception(msg)
        

class MakoInstaller(Installer):
    """ Exactly like ``paste.script.command.Installer`` except for
    configuration file generation.

    The ``.ini`` is rendered with Mako and the user is prompted for
    required values.  The class variables ``required_vals` is a list
    of value names or argument tuples passed to the contructor of
    IniOpt."""

    use_cheetah = False
    meta_name = "paste_deploy_config.ini_tmpl"
    
    required_vals = []

    def config_content(self, command, vars):
        """
        Called by ``self.write_config``, this returns the text content
        for the config file, given the provided variables.

        This implementation reads
        ``Package.egg-info/paste_deploy_config.ini_tmpl`` and fills it
        with the variables using Mako.
        """

        # TODO: There is a lot of cleenup that can be done when the
        # next paste script is out.  1: we can subclass
        # .template_renderer()

        for param in self.required_vals:
            if isinstance(param, str) or isinstance(param, unicode):
                opt = IniOpt(param)
            else:
                opt = IniOpt(*param)
            opt.request(vars, command)
        
        if not self.dist.has_metadata(self.meta_name):
            if command.verbose:
                print 'No %s found' % meta_name
            return self.simple_config(vars)

        tmpl = Template(self.dist.get_metadata(self.meta_name))
        return copydir.careful_sub(
            tmpl.render_unicode(**vars), vars, self.meta_name)


from uuid import uuid1
from hashlib import sha1
from datetime import date

def shahex(vars):
    return sha1(str(uuid1())).hexdigest()

def getuuid(vars):
    return str(uuid1())

# a list of (coerce_funct, opt1, opt2, ...) tuples
OPTIONS_COERCE = [(asbool, "staging", "use_google_search", "site_readonly"),
                  (int, "nb_site_proxy"),
                  (parse_timedelta, "wiki_indexing_delay"),
                  ]

class GazestInstaller(MakoInstaller):
    required_vals = [("site_name", "Another Gazest Site"),
                     "domain_name",
                     ("site_base",
                      lambda v:"http://gazest.%s" % v["domain_name"]),
                     ("port", 8082),
                     ("site_uuid", getuuid, False),
                     ("site_changes_feed_uuid", getuuid, False),
                     ("webmaster_email",
                      lambda v:"webmaster@%s" % v["domain_name"]),
                     ("error_email_from",
                      lambda v:"paste@%s" % v["domain_name"]),
                     ("system_email_from",
                      lambda v:"no-reply@%s" % v["domain_name"]),
                     ("smtp_server", "localhost"),
                     ("copyright_years", date.today().year),
                     "copyright_owner",
                     ("copyright_owner_email", lambda v:v["webmaster_email"]),
                     ("beaker_session_key", "gazest"),
                     ("beaker_session_secret", shahex, False),
                     ("authkit_cookie_secret", shahex, False),
                     ("sqlalchemy_url", "sqlite:///%(here)s/data.db"),
                     ("use_mod_proxy", True,
                      "site behind mod_proxy or mod_rewrite"),
                     ("nb_site_proxy",
                      lambda vars:vars["use_mod_proxy"] and 1 or 0,
                      False),
                     ("wiki_indexing_delay", "5d"),
                     ("use_error_mails", False),
                     ("staging", True),
                     ("use_google_search", True),
                     ]


def deploy_config(cmd, basename, filename):
    template = dirname(__file__) + '/' + basename
    cmd.write_file('config template', filename, open(template).read())

