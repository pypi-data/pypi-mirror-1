from setuptools import setup, find_packages

setup(
    name = 'largeblue.util',
    version = '0.1',
    description = "Some helpful web dev utilities",
    long_description = '/n%s' % open('src/largeblue/util/README.txt', 'r').read(),
    keywords = 'zope largeblue util utilities batch email',
    author = 'James Arthur',
    author_email = 'firstname.lastname@largeblue.com',
    url = 'http://pesto.largeblue.net/trac/browser/largeblue/devel/largeblue.util',
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
        'zope.app.appsetup',
        'zope.app.testing',
        'zope.app.wsgi>=3.4.0',
        'zope.app.zcmlfiles',
        'zope.app.securitypolicy',
        'zope.i18n',
        'zope.security',
        'zope.testing',
        'zope.sendmail'
    ],
    entry_points = """
        [console_scripts]
        largeblue-debug = largeblue.startup:interactive_debug_prompt
        largeblue-ctl = largeblue.startup:zdaemon_controller
        [paste.app_factory]
        main = largeblue.startup:application_factory
    """
)
