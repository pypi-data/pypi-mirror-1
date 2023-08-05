usage: subzilla [options] bug [description]

subzilla will post a patch from a Subversion tree to a Bugzilla bug, apply a
patch from a Bugzilla bug to a Subversion tree, or close the given bug.

options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -a, --apply           apply a patch from bug [default: True]
  -p, --post            post the current Subversion diff
  -c, --close           close the bug
  -d, --use-current-dir
                        restrict posted diff to the current directory
  -r RESTRICT, --restrict-diff=RESTRICT
                        restrict posteddiff to the given directory or file
                        (overrides -d)
  --patch-number=PATCH_NUMBER
                        which patch should be applied (the default, -1, means
                        last)
  -f FILE, --file=FILE  read configuration from FILE [default: ~/.subzilla]
  -v, --verbose         
  -j PROJECT, --project=PROJECT
                        read options from PROJECT in the config file
  --force-prompt        force prompt to input options and overwrite config
                        file
  --preserve            don't obsolete existing patches
