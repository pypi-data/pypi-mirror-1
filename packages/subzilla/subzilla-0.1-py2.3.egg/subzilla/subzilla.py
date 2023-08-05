#!/usr/bin/env python
"""subzilla, a utility for working with Subversion and Bugzilla.

subzilla requires that twill be installed, and that svn and patch be in
your path.

"""
import twill, os, StringIO
import ConfigParser, getpass
from optparse import OptionParser
import re

version = '0.1'

class Options(object):
    
    def add(self, otherOptions, override=False):
        for key, val in otherOptions.__dict__.iteritems():
            if override or not hasattr(self, key):
                setattr(self, key, val)

default = Options()
default.cookie_file     = "~/.subzilla_cookie"
default.ini_file        = "~/.subzilla"
# OSAF's bugzilla should be the default, but we want to prompt
# once to use it, so name it default.defaulturl, not default.url
default.defaulturl      = "https://bugzilla.osafoundation.org/"

options = Options()

def main():
    global browser, state, attachment_page, initial_url, description
    if not getOptions():
        return

    attachment_page = "attachment.cgi"
    show_bug_page   = "show_bug.cgi"
    if options.apply or options.close:
        initial_url="%s%s?id=%s" % (options.url, show_bug_page,
                                       bug_number)
    else:
        initial_url="%s%s?bugid=%s&action=enter" % (options.url,
                                                    attachment_page,
                                                    bug_number)

    browser = twill.browser.TwillBrowser()
    state = browser._browser

    # twill wants to print a whole bunch of information, don't let it
    if not options.verbose:
        twill.browser.OUT = os.tmpfile()

    if options.post:
        # before going to the network, check if there's anything to do

        if options.restrict is not None:
            restrict = options.restrict
        elif options.use_current:
            restrict = os.getcwd()
        else:
            restrict = options.subversion_root            

        diff = get_diff(options.subversion_root, restrict)
        if diff is None:
            print "no local changes in %s" % restrict
            return

    # go to the first page
    start(initial_url)

    if options.apply:
        apply_patch(get_patch(), options.subversion_root) 

    elif options.post:
        # post a diff
        while description == "":
            description = raw_input("Patch description (cannot be blank): ")
        comment = raw_input("Patch comment (optional): ")
        reviewer = raw_input("Request review from (optional): ")
        if options.verbose:
            print "Submitting patch for bug %s" % bug_number
            if options.obsolete:
                print "Obsoleting any existing patches"
        post_patch('Subzilla_%s.diff' % bug_number, diff, description, comment,
                   options.obsolete, reviewer)

    elif options.close:
        close_bug()

def start(initial_url):
    try:
        browser.load_cookies(os.path.expanduser(options.cookie_file))
        if options.verbose:
            print "using cookies"
    except IOError:
        pass
    browser.go(initial_url)

def getName(name):
    return browser.get_form_field(state.form, name)

def login():
    # find the appropriate form, for now just assume it's form 0
    controls = state.forms()[0].controls
    controls[0].value = options.username
    controls[1].value = options.password
    browser.submit(None)
    browser.save_cookies(os.path.expanduser(options.cookie_file))

def close_bug():
    # find the appropriate form, for now just assume it's form 0
    state.form = state.forms()[0]
    # we may have been logged in via cookie, if not, login
    if state.form.controls[0].name == "Bugzilla_login":
        login()
        state.form = state.forms()[0]

    rev = get_revision(options.subversion_root)
    if rev is not None:
        default = "Fixed in r%s." % rev
    else:
        default = "Fixed."
    comment = raw_input("Close comment [default: %s]: " % default)
    if comment == '':
        comment = default

    getName('knob').get('resolve').selected = True
    getName('resolution').get('FIXED').selected = True
    getName('comment').value = comment

    browser.submit(None)
    print
    print "Bug closed."


def post_patch(filename, filestream, description, comment=None,
               obsolete_old = True, reviewer = ''):
    # find the appropriate form, for now just assume it's form 0
    state.form = state.forms()[0]
    # we may have been logged in via cookie, if not, login
    if state.form.controls[0].name == "Bugzilla_login":
        login()
        state.form = state.forms()[0]

    # set patch, file, and description fields
    getName('ispatch').items[0].selected = True
    getName('data').add_file(filestream, filename=filename)
    getName('description').value = description
    if comment is not None:
        getName('comment').value = comment

    if obsolete_old:
        try:
            for i in getName('obsolete').items:
                i.selected = True
        except:
            pass

    if reviewer != '':
         getName('flag_type-2').get('?').selected = True 
         getName('requestee_type-2').value = reviewer

    browser.submit(None)
    print
    print "Patch posted."

def get_diff(svn_root, path):
    path     = os.path.abspath(os.path.expanduser(path))
    svn_root = os.path.normpath(os.path.expanduser(svn_root))
    if options.verbose:
        print "Using %s for svn_root" % svn_root
        print "Getting diff from %s" % path
    if path.find(svn_root) != 0:
        # path isn't in svn_root
        return None
    # after norm_path, svn_root will not contain a trailing slash
    # so chop off one more character than len(svn_root)
    rel_path = path[len(svn_root) + 1:]
    diff_cmd = "cd %s; svn diff %s" % (svn_root, rel_path)
    diff = StringIO.StringIO(os.popen(diff_cmd).read())
    if diff.read(1) == "":
        return None
    else:
        diff.seek(0)
        return diff

def get_revision(svn_root):
    info_cmd = "cd %s; svn info" % svn_root
    info = StringIO.StringIO(os.popen(info_cmd).read())
    for line in info.readlines():
        if line.startswith('Revision'):
            return line.split()[-1]
    return None

link_pat = re.compile('attachment\.cgi\?id=\d*$')

def get_patch():
    links = [l for l in state.links() if link_pat.match(l.url)]
    if len(links) == 0:
        print "No attachments found for bug %s, quitting" % bug_number
    else:
        position = options.patch_number
        browser.follow_link(links[position])
        return browser.get_html()

def apply_patch(patch, path):
    patch_cmd = "cd %s; patch -up0" % path
    input, info = os.popen4(patch_cmd)
    input.write(patch)
    input.close()
    for line in info.readlines():
        print line

def inSVN(path):
    info_cmd = "cd %s; svn info" % path
    # use popen4 to read in stderr
    input, info = os.popen4(info_cmd)
    for line in info.readlines():
        if line[:4] == "URL:":
            return True
    return False

def getOptions():
    ##### Configuration options #####

    global bug_number, description

    usage = "usage: %prog [options] bug [description]"
    parser = OptionParser(usage=usage, version=version)
    parser.set_description(
        "subzilla will post a patch from a Subversion tree "
        "to a Bugzilla bug, apply a patch from a Bugzilla "
        "bug to a Subversion tree, or close the given bug.")

    parser.set_defaults(verbose=False, apply=False, post=False, close=False,
                        prompt=False, obsolete=True)

    parser.add_option("-a", "--apply", dest="apply", action="store_true",
                      help="apply a patch from bug [default: True]")

    parser.add_option("-p", "--post", dest="post", action="store_true",
                      help="post the current Subversion diff")

    parser.add_option("-c", "--close", dest="close", action="store_true",
                      help="close the bug")

    parser.add_option("-d", "--use-current-dir", dest="use_current",
                      default=False, action="store_true",
                      help="restrict posted diff to the current directory")

    parser.add_option("-r", "--restrict-diff", dest="restrict",
                      help="restrict posteddiff to the given directory or file "
                           "(overrides -d)")

    parser.add_option("--patch-number", dest="patch_number", default=-1,
                      type='int', help="which patch should be applied "
                                       "(the default, -1, means last)")

    parser.add_option("-f", "--file", dest="ini_file",
                      default=default.ini_file, metavar="FILE",
                      help="read configuration from FILE [default: %default]")
    
    parser.add_option("-v", "--verbose", default=False,
                      action="store_true", dest="verbose")

    parser.add_option("-j", "--project", dest="project",
                      help="read options from PROJECT in the config file")

    parser.add_option("--force-prompt", dest="prompt", action="store_true",
                      help="force prompt to input options and overwrite " 
                           "config file")

    parser.add_option("--preserve", dest="obsolete", default=True,
                      action="store_false",
                      help="don't obsolete existing patches") 

    (cmdline_options, args) = parser.parse_args()
    if len(args) < 1:
        print "error: too few arguments given"
        print
        print parser.format_help()
        return False

    bug_number = args[0]
    if len(args) > 1:
        description = args[1]
    else:
        description = ''

    if not cmdline_options.close and not cmdline_options.post:
        cmdline_options.apply = True
    
    cfg = ConfigParser.SafeConfigParser()
    cfg.read(os.path.expanduser(cmdline_options.ini_file))
    
    cfg_options = Options()
    section_used = None
    project = getattr(cmdline_options, 'project', None)
    for section in cfg.sections():
        if project is not None:
          if project == section:
              section_used = section
        elif cfg.has_option(section, 'subversion_root'):
            expanded = os.path.expanduser(cfg.get(section, 'subversion_root'))
            root = os.path.normpath(expanded)
            if os.path.commonprefix([root, os.getcwd()]) == root:
                section_used = section
        if section_used is not None:
            for key, val in cfg.items(section):
                if cmdline_options.verbose:
                    if key == 'password':
                        print "Loading %s as: %s" % (key, '****')
                    else:
                        print "Loading %s as: %s" % (key, val)
                setattr(cfg_options, key, val)
            break

    options.add(cmdline_options)
    options.add(cfg_options)
    options.add(default)

    if project is None and not inSVN(os.getcwd()):
        print "error: not in a subversion tree and no project given"
        print
        print parser.format_help()
        return False

    ##### Prompt the user for options, if appropriate #####

    prompted = Options()
    
    if options.prompt or not hasattr(options, 'url'):
        prompted.url = raw_input(
            "Base Bugzilla URL [default %s]:\n"
            % options.defaulturl)
        if prompted.url == '':
            prompted.url = options.defaulturl

    if options.prompt or not hasattr(options, 'username'):
        prompted.username = raw_input("Username: ")
    if options.prompt or not hasattr(options, 'password'):
        prompted.password = getpass.getpass()
    if options.prompt or not hasattr(options, 'subversion_root'):
        current = os.getcwd()
        prompted.subversion_root = raw_input("Subversion home [%s]: "
                                             % current)
        if prompted.subversion_root == '':
            prompted.subversion_root = current

    if options.prompt or len(prompted.__dict__) > 0:
        msg ="Save project to %s [y]/n (password will be stored in plaintext)? "
        should_save = raw_input(msg % options.ini_file)
        if should_save.lower() in ("", "y"):
            project_name = raw_input("Project name: ").lower()
            if not cfg.has_section(project_name):
                cfg.add_section(project_name)

            for key, val in prompted.__dict__.iteritems():
                cfg.set(project_name, key, val)
                f = file(os.path.expanduser(cmdline_options.ini_file), 'w')
                cfg.write(f)
                f.close()

    options.add(prompted, override=True)
    # make sure the base url is terminated with a slash character
    if options.url[-1] != '/':
        options.url += '/'

    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print "Aborted"
              
