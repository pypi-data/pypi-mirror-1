#!/usr/bin/env python

from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

setup(
    name='TGPriFlash',
    version='0.1.2',
    description='A TurboGears flash implementation that supports multiple priority levels.',
    long_description="""\
TGPriFlash is a TurboGears flash implementation that supports multiple
priority levels.

Out of the box, 3 levels are defined (FLASH_INFO, FLASH_WARNING,
FLASH_ALERT) but you can ignore these and use any integer values
you like as the flash priority levels.

To "magically" replace (aka monkey patch) turbogears.flash() with
this one, just add this import to your start-project.py::

    import tg_pri_flash.flash

Within your project you can import turbogears.flash as normal::

    from turbogears import flash

You'll want to replace the tg_flash line in your master template::

    <div py:if="tg_flash" class="flash" py:content="tg_flash"></div>

with something like this::

    <div py:if="tg_flash and tg_flash[1]==0" class="flash_ok" py:content="tg_flash[0]"></div>
    <div py:if="tg_flash and tg_flash[1]==1" class="flash_warning" py:content="tg_flash[0]"></div>
    <div py:if="tg_flash and tg_flash[1]==2" class="flash_alert" py:content="tg_flash[0]"></div>

You would then define CSS definitions for each of the classes.

In your controller you can call flash() with a second argument, a positive integer::

    flash( _(u"There was an error"), 2 )

or, using the built-in constants::

    from tg_pri_flash.flash import FLASH_ALERT
    flash( _(u"There was an error"), FLASH_ALERT )
""",
    author='Chris Miles',
    author_email='miles.chris@gmail.com',
    url='http://www.psychofx.com/turbogears/TGPriFlash/',
    license='MIT',
    packages=['tg_pri_flash'],
    install_requires = ["TurboGears>=1.0.1"],
    include_package_data = True,
    zip_safe=False,
    keywords = [
        'turbogears.widgets',
    ],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Framework :: TurboGears',
        'Framework :: TurboGears :: Widgets',
    ],
)
