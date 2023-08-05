from setuptools import setup, find_packages
setup(
    name = "subzilla",
    version = "0.1.1",
    packages = find_packages(),
    install_requires = ['twill>=0.8.0'],
    entry_points = { 'console_scripts': ['subzilla = subzilla.subzilla:main'] },
    url = 'http://svn.osafoundation.org/sandbox/jeffrey/subzilla/README.txt',
    author = 'Jeffrey Harris',
    description = 'Subzilla will post a patch from a Subversion tree to a ' \
                  'Bugzilla bug, apply a patch from a Bugzilla bug to a ' \
                  'Subversion tree, or close a Bugzilla bug.',
    long_description = """Development has focused on connecting to OSAF's
                          Bugzilla instance, but it ought to work with
                          reasonable Bugzilla instances.""",
    classifiers = [
      'Development Status :: 3 - Alpha',
      'Environment :: Console',
      'Environment :: Web Environment',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: Python Software Foundation License',
      'Programming Language :: Python',
      'Topic :: Software Development :: Bug Tracking',
      ],
)
