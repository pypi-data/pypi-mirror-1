
from paste.script.appinstall import Installer
from mako.template import Template
from paste.script import copydir
from paste.script.command import NoDefault
from pprint import pprint
from os.path import dirname

class MakoInstaller(Installer):
    """ Exactly like ``paste.script.command.Installer`` except for
    configuration file generation.

    The ``.ini`` is rendered with Mako and the user is prompted for
    required values.  The class variables ``required_vals` and
    ``required_bool_vals`` are lists of value names or ``(val_name,
    default)`` tuples.  If ``default`` is callable, it will be called
    with the ``vars`` dict to the the default; otherwise, its value is used
    literally."""

    # TODO: better prompts, possibly with terse prompts and added
    # supper in .ask() for 'h' to generate long help.
    
    use_cheetah = False
    meta_name = "paste_deploy_config.ini_tmpl"
    
    #required_vals = []
    #required_bool_vals = []
    

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
        # .template_renderer() 2: .ask() will support NoDefault
        # instead of 'none'

        vals_stuff = [(val, command.challenge, NoDefault)
                      for val in self.required_vals]
        vals_stuff += [(val, command.ask, 'none')
                      for val in self.required_bool_vals]
        
        for val, prompt_f, no_default in vals_stuff:
            default = no_default
            if isinstance(val, tuple) or isinstance(val, list):
                val, default = val
                if callable(default):
                    default = default(vars)

            if val not in vars:
                if  command.interactive:
                    vars[val] = prompt_f(val, default=default)
                elif default is not no_default:
                    vars[val] = default
                else:
                    msg = "Can't generate configuration: '%s' missing" % val
                    raise Exception(msg)

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

class GazestInstaller(MakoInstaller):
    required_vals = [("site_name", "A Gazest Site"),
                     "domain_name",
                     ("site_base",
                      lambda v:"http://gazest.%s" % v["domain_name"]),
                     ("port", 8082),
                     ("site_uuid", getuuid),
                     ("site_changes_feed_uuid", getuuid),
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
                     ("beaker_session_secret", shahex),
                     ("authkit_cookie_secret", shahex),
                     ("sqlalchemy_dburi", "sqlite:///%(here)s/data.db"),
                     ]

    required_bool_vals = [("use_error_mails", False),
                          ("staging", True),
                          ]

def deploy_config(cmd, basename, filename):
    template = dirname(__file__) + '/' + basename
    cmd.write_file('config template', filename, open(template).read())

