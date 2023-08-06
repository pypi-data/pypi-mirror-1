from setuptools import setup, find_packages
from os.path    import dirname, join
srcdir = join(dirname(__file__), 'src')
setup(name             = 'SpiffGuard',
      version          = '1.9.2',
      description      = 'A Generic Access List Library',
      long_description = \
"""
Spiff Guard is a library implementing generic access lists for Python.
It was designed to provide a clean API, high security and high
scalability. Working with an ACL is as simple as this:

::

    from Guard import *
    guard   = DB(db_connection)
    group   = ResourceGroup("My Group")
    user    = Resource("My User")
    website = ResourceGroup("My Website")
    view    = Action("View")
    write   = Action("Edit")
    guard.register_type([Resource, ResourceGroup, Website])
    guard.add_action([view, write])
    guard.add_resource([user, group, website])
    guard.grant(group, view, website)
    guard.grant(user,  edit, website)
    if guard.has_permission(user, view, website):
        print 'Permission granted.'

Spiff Guard's features include recursion, groups, Python type awareness,
inverse lookup, and a lot more. For a more complete example, have a look
into the `README file`_ included with the package. You may also look at the
`API documentation`_.

.. _README file: http://code.google.com/p/spiff-guard/source/browse/trunk/README
.. _API documentation: http://spiff.debain.org/static/docs/spiff_guard/index.html
""",
      author           = 'Samuel Abels',
      author_email     = 'cheeseshop.python.org@debain.org',
      license          = 'GPLv2',
      package_dir      = {'': srcdir},
      packages         = [p for p in find_packages(srcdir)],
      install_requires = ['sqlalchemy'],
      keywords         = 'spiff guard acl acls security authentication object storage',
      url              = 'http://code.google.com/p/spiff-guard/',
      classifiers      = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        'Topic :: Security',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules'
      ])
