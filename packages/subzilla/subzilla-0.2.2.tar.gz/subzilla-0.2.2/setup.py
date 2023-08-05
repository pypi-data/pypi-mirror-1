from setuptools import setup, find_packages
setup(
    name = "subzilla",
    version = "0.2.2",
    packages = find_packages(),
    install_requires = ['twill>=0.9b1'],
    entry_points = { 'console_scripts': ['subzilla = subzilla.subzilla:main'] },
    url = 'http://svn.osafoundation.org/sandbox/jeffrey/subzilla/README.txt',
    author = 'Jeffrey Harris',
    description = 'Subzilla will post a patch from a Subversion tree to a ' \
                  'Bugzilla 3.0 bug, or apply a patch from a Bugzilla bug to a ' \
                  'Subversion tree.',
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
