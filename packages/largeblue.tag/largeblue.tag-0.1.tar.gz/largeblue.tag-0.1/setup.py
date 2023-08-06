from setuptools import setup, find_packages

setup(
    name = 'largeblue.tag',
    version = '0.1',
    description = "Simple tagging adapter",
    long_description = '\n%s' % open("src/largeblue/tag/README.txt").read(),
    keywords = 'zope largeblue tag tags tagging adapter simple',
    author = 'James Arthur',
    author_email = 'firstname.lastname@largeblue.com',
    url = 'http://pesto.largeblue.net/trac/browser/largeblue/devel/largeblue.tag',
    license = 'Public Domain',
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
    namespace_packages = ['largeblue'],
    package_dir = {'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'ZConfig',
        'zdaemon',
        'ZODB3',
        'zope.annotation',
        'zope.app.appsetup',
        'zope.app.authentication',
        'zope.app.catalog',
        'zope.app.tree',
        'zope.app.intid',
        'zope.app.keyreference',
        'zope.app.testing',
        'zope.app.wsgi>=3.4.0',
        'zope.app.zcmlfiles',
        'zope.app.securitypolicy',
        'zope.copypastemove',
        'zope.formlib',
        'zope.i18n',
        'zope.publisher',
        'zope.security',
        'zope.testing',
        'zope.traversing'
    ],
    entry_points = """
        [console_scripts]
        largeblue-debug = largeblue.startup:interactive_debug_prompt
        largeblue-ctl = largeblue.startup:zdaemon_controller
        [paste.app_factory]
        main = largeblue.startup:application_factory
    """
)
