from setuptools import setup, find_packages

setup(
    name = 'largeblue.pages',
    version = '0.3.1',
    description = "A simple approach to making a zope website's pages content managable",
    long_description = '\n%s' % open("src/largeblue/pages/README.txt").read(),
    keywords = 'zope largeblue pages cms wysiwyg webdav orderable',
    author = 'James Arthur',
    author_email = 'firstname.lastname@largeblue.com',
    url = 'http://pesto.largeblue.net/trac/browser/largeblue/devel/largeblue.pages',
    license = 'Public Domain (note, vendor code contained within has own licenses)',
    classifiers = [
        'Programming Language :: Python',
        'Environment :: Web Environment',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Framework :: Zope3',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Natural Language :: English',
    ],
    packages=find_packages('src'),
    namespace_packages = ['largeblue', 'bebop'],
    package_dir = {'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'elementtree',
        'setuptools',
        'ZConfig',
        'zdaemon',
        'ZODB3',
        'z3c.dav',
        'z3c.davapp.zopeappfile',
        'z3c.davapp.zopelocking',
        'z3c.etree',
        'z3c.widget',
        'zc.resourcelibrary',
        'zope.annotation',
        'zope.app.appsetup',
        'zope.app.authentication',
        'zope.app.catalog',
        'zope.app.dav',
        'zope.app.file',
        'zope.app.folder',
        'zope.app.tree',
        'zope.app.intid',
        'zope.app.keyreference',
        'zope.app.testing',
        'zope.app.wsgi>=3.4.0',
        'zope.app.zcmlfiles',
        'zope.app.securitypolicy',
        'zope.copypastemove',
        'zope.filerepresentation',
        'zope.formlib',
        'zope.i18n',
        'zope.locking',
        'zope.publisher',
        'zope.security',
        'zope.testing',
        'zope.traversing',
        'largeblue.order'
    ],
    entry_points = """
        [console_scripts]
        largeblue-debug = largeblue.startup:interactive_debug_prompt
        largeblue-ctl = largeblue.startup:zdaemon_controller
        [paste.app_factory]
        main = largeblue.startup:application_factory
    """
)