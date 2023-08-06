from setuptools import setup, find_packages

setup(
    name = "DzenStatus",
    version = "0.1.2",
    py_modules = [ 'dzenstatus' ],
    package_data = {
        '': [ '*.ini' ],        # For example config.
    }, 

    entry_points = {
        'gui_scripts': [
            'dzenstatus = dzenstatus:main_run_dzen',
        ],
        'console_scripts': [
            'dzenstatus_pipe = dzenstatus:main_pipe',
        ],
        # Allows using the egg *without* installing.
        'setuptools.installation': [
            'eggsecutable = dzenstatus:main_run_dzen',
        ],
        'dzenstatus.plugins.v1': [
            'static = dzenstatus:plugin_static',
            'read_fd = dzenstatus:plugin_read_fd',
            'gmail_feed = dzenstatus:plugin_gmail_feed',
            'wifi = dzenstatus:plugin_wifi',
            'acpi_battery = dzenstatus:plugin_battery',
            'clock = dzenstatus:plugin_clock',
            'spaces = dzenstatus:plugin_spaces',
        ],
    },

    author = "Greg S.",
    author_email = "enimihil@gmail.com",
    description = "A flexible (setuptools) plugin-based script for use creating dzen2 status bars.",
    license = "GPL",
    keywords = "status dzen dzen2 statusbar",
    url = "http://tthanna.enimihil.net/pub/hg/dzenstatus",

    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: X11 Applications',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Topic :: Desktop Environment',
        'Topic :: System :: Monitoring',
        'Topic :: Utilities',
    ],

    long_description = open('doc.rst').read(),
)
