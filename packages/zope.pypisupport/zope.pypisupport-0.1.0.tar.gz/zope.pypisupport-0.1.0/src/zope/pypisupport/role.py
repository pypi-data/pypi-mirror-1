##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""PyPI Role Management
"""
import sys
import optparse
import base64
import lxml.etree
import mechanize
import zope.testbrowser.browser

BASE_URL = 'http://pypi.python.org/pypi/'

ALL_PACKAGES_XPATH = ("//html:div[@id='document-navigation']/"
                      "html:ul/html:li[position()=1]/html:a/text()")
PACKAGE_DISTS_XPATH = "//html:table[@class='list']/html:tr/html:td/html:a/@href"
NS_MAP = {'html': 'http://www.w3.org/1999/xhtml'}

def getPackages(options, browser):
    if not options.allPackages:
        return options.packages
    browser.open(BASE_URL)
    tree = lxml.etree.fromstring(browser.contents)
    return tree.xpath(ALL_PACKAGES_XPATH, NS_MAP)

def changeRole(browser, user, action):
    # Try to get to the admin link and click it.
     try:
         browser.getLink('admin', index=0).click()
     except mechanize._mechanize.LinkNotFoundError:
         print '    +-> Error/Warning: admin link not found'
         return
     # Fill in the user whose roles are modified.
     browser.getControl(name='user_name').value = user
     # Execute the action
     try:
         browser.getControl(action + ' Role').click()
     except Exception, err:
         msg = err.read().strip().split('\n')[-1]
         print '    +-> Error/Warning: ' + msg

def manipulateRole(options):
    # Create a browser instance.
    browser = zope.testbrowser.browser.Browser()
    # Log in as the specified user.
    creds = base64.b64encode('%s:%s' %(options.username, options.password))
    browser.addHeader('Authorization', 'Basic ' + creds)
    # Execute the action for each specified package.
    for package in getPackages(options, browser):
        url = BASE_URL + package
        print '%s %s as Owner to: %s' %(options.action, options.targetUser, url)
        try:
            browser.open(url)
        except Exception, err:
            print '    +-> Error/Warning: package does not exist'
            continue
        # Some packages list all of their versions
        if 'Index of Packages' in browser.contents:
            tree = lxml.etree.fromstring(browser.contents)
            for href in tree.xpath(PACKAGE_DISTS_XPATH, NS_MAP):
                browser.open(href)
                changeRole(browser, options.targetUser, options.action)
        else:
            changeRole(browser, options.targetUser, options.action)

###############################################################################
# Command-line UI

parser = optparse.OptionParser("%prog [options] USERNAME [PACKAGE, ...]")

config = optparse.OptionGroup(
    parser, "Configuration", "Options that deal with configuring the browser.")

config.add_option(
    '--username', '--user', action="store", dest='username',
    help="""Username to access the PyPI Web site.""")

config.add_option(
    '--password', '--pwd', action="store", dest='password',
    help="""Password to access the PyPI Web site.""")

config.add_option(
    '--all', '-a', action="store_true", dest='allPackages',
    help=("When specified, all packages that the user has access "
          "to are modified."))

# Default setup
default_setup_args = []

def merge_options(options, defaults):
    odict = options.__dict__
    for name, value in defaults.__dict__.items():
        if (value is not None) and (odict[name] is None):
            odict[name] = value

def get_options(args=None, defaults=None):

    default_setup, _ = parser.parse_args(default_setup_args)
    assert not _
    if defaults:
        defaults, _ = parser.parse_args(defaults)
        assert not _
        merge_options(defaults, default_setup)
    else:
        defaults = default_setup

    if args is None:
        args = sys.argv
    original_args = args
    options, positional = parser.parse_args(args)
    merge_options(options, defaults)
    options.original_args = original_args

    if not positional or len(positional) < 1:
        parser.error("No target user and/or packages specified.")
    options.targetUser = positional[0]
    options.packages = positional[1:]

    return options

# Command-line UI
###############################################################################

def addrole(args=None):
    if args is None:
        args = sys.argv[1:]

    options = get_options(args)
    options.action = 'Add'
    manipulateRole(options)

def delrole(args=None):
    if args is None:
        args = sys.argv[1:]

    options = get_options(args)
    options.action = 'Remove'
    manipulateRole(options)
