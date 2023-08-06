#!/usr/bin/env python
"""
TOPP's OpenPlans site initialization tool
"""
from optparse import OptionParser
#from cmdutils import main_func
#from cmdutils import CommandError
from ConfigParser import ConfigParser
import os
import pwd
import re
import string
import subprocess
import sys
import tempita

description = """\
%prog bootstraps OpenPlans site installations.  It constructs an
initial directory structure to house the underlying software,
including a 'newbuild' script which will create, download, and build
said software.  Also optionally generates a sample Apache
configuration which can be added to an existing httpd.conf file.
"""

script_dir = os.path.dirname(__file__)

parser = OptionParser(
    usage="%prog [OPTIONS] SITE_FQDN BASE_PORT VARIABLES",
    description=description,
    )

parser.add_option(
    '-c', '--config',
    dest='config',
    action='store',
    default=os.path.join(script_dir, 'newsite.ini'),
    help='Config file to load',
    )

parser.add_option(
    '-A', '--apache-conf-outfile',
    dest='apache_conf_outfile',
    action='store',
    help='File into which Apache vhost config should be written',
    default='apache.conf',
    )

conf = ConfigParser()

def to_bool(value):
    """ turns a config option (a string) into a boolean value"""
    if not value: # accept None
        return False
    return conf._boolean_states.get(value.lower(), False)

_var_re = re.compile(r'^(?:\[(\w+)\])?\s*(\w+)=(.*)$')
_dot_var_re = re.compile(r'^(\w+)\.(\w+)=([^=>].*)$')
def parse_positional(args):
    """
    Parses out the positional arguments into fassembler projects and
    variable assignments.
    """
    nonvar_args = []
    variables = []
    for arg in args:
        match = _var_re.search(arg)
        if match:
            variables.append(('general', match.group(2), match.group(3)))
        else:
            match = _dot_var_re.search(arg)
            if match:
                variables.append((match.group(1), match.group(2), match.group(3)))
            else:
                nonvar_args.append(arg)
    return nonvar_args, variables

def append_under(value):
    """
    appends an underscore to the string, but only if it's non-empty
    (used in the template)
    """
    if value:
        return value + '_'
    return value

def assert_svn_repo_exists(url):
    command = subprocess.Popen(['svn', 'ls', url],
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = command.communicate()
    errcode = command.wait()
    if errcode:
        sys.stderr.write(stdout)
        return False
    return True

def main():
    """
    Implements the command-line new site script.
    """
    # validation and initialization
    options, args = parser.parse_args()
    args, variables = parse_positional(args)
    if len(args) < 2:
        parser.error("You must provide both SITE_FQDN and BASE_PORT")

    site_fqdn = args[0]
    base_port = args[1]

    config_map = {}
    ini_path = options.config
    if os.path.exists(ini_path):
        conf.read(ini_path)
        config_map = conf._sections

    for section, key, value in variables:
        if not config_map.has_key(section):
            config_map[section] = {}
        config_map[section].update({key:value})

    general = config_map.get('general', {})

    # do we require a specific user?
    real_user = pwd.getpwuid(os.getuid())[0]
    user_enforced = general.has_key('req_user')
    req_user = general.get('req_user', real_user)
    if real_user != req_user:
        parser.error("You must run this as the '%s' user" % req_user)

    # make sure we have an etc_svn_repo URL before we get any further
    etc_svn_repo = general.get('etc_svn_repo', '').strip()
    while not etc_svn_repo:
        # this one is so important we prompt the user interactively
        prompt = '\n'.join(("Please enter a URL for your configuration svn repository",
                            "(i.e. the 'etc_svn_repo'). Because this will contain",
                            "possibly sensitive configuration information, it is",
                            "recommended that this repository NOT be readable by",
                            "untrusted users.:\n"))
        etc_svn_repo = raw_input(prompt).strip()

    if not assert_svn_repo_exists(etc_svn_repo):
        sys.stderr.write("Error: couldn't verify subversion at %r!\n"
                         % etc_svn_repo)
        sys.exit(1)

    # calculate install directory name (either fqdn or port number)
    base_dir = general.get('base_dir', os.getcwd())
    dirname = site_fqdn
    if to_bool(general.get('use_port_for_dirname')):
        dirname = base_port
    install_dir = os.path.join(base_dir, dirname)

    # create directory structure
    subs = {'dir': install_dir}
    print 'Making directories "%(dir)s" "%(dir)s/builds" "%(dir)s/var"' \
          % subs
    os.makedirs("%(dir)s/builds" % subs)
    os.makedirs("%(dir)s/var" % subs)
    newbuildpath = "%(dir)s/newbuild.sh" % subs

    # create base_port.txt
    outfile = open('%(dir)s/base_port.txt' % subs, 'w')
    outfile.write(str(base_port))
    outfile.close()

    # prep the substitutions for newbuild.sh
    force_ssl = str(to_bool(general.get('force_ssl')))
    home_dir = pwd.getpwnam(req_user)[5]
    subs = {'base_dir': install_dir, 'req_user': req_user,
            'append_under': append_under, 'force_ssl': force_ssl,
            'etc_svn_prefix': general.get('etc_svn_prefix', ''),
            'home_dir': home_dir, 'extra_path': general.get('extra_path', ''),
            'user_enforced': user_enforced, 'etc_svn_repo': etc_svn_repo,
            }

    # create newbuild.sh
    print "\nCreating %s" % newbuildpath
    newbuild_tmpl_path = os.path.join(script_dir, 'newbuild.sh.template')
    newbuild_tmpl = tempita.Template.from_filename(newbuild_tmpl_path)
    outfile = open(newbuildpath, 'w')
    outfile.write(newbuild_tmpl.substitute(subs))
    outfile.close()
    os.chmod(newbuildpath, 0755)

    if config_map.has_key('apache'):
        # write apache config
        outfile_path = options.apache_conf_outfile
        if not outfile_path.startswith(os.path.sep):
            outfile_path = os.path.join(install_dir, outfile_path)
        print "Writing Apache config to %s" % outfile_path

        apache = config_map.get('apache', {})
        ip = apache.get('ip', '127.0.0.1')
        rootfqdn = site_fqdn.split('.')
        rootfqdn[0] = rootfqdn[0] + 'root'
        rootfqdn = '.'.join(rootfqdn)

        apache_conf_infile = open(os.path.join(script_dir,
                                               'apacheconf.template'))
        apache_conf_tmpl = string.Template(apache_conf_infile.read())
        apache_conf = apache_conf_tmpl.safe_substitute(ip=ip,
                                                       site_fqdn=site_fqdn,
                                                       siteroot_fqdn=rootfqdn,
                                                       zope_port=int(base_port)+1,
                                                       )
        apache_conf_outfile = open(outfile_path, 'w')
        apache_conf_outfile.write(apache_conf)
        apache_conf_outfile.close()

    print("\nSuccess; site layout setup in %(dir)s\n"
          "Run %(dir)s/newbuild.sh to continue" % {'dir': install_dir})

if __name__ == '__main__':
    main()
