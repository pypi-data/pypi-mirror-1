# -*- coding: UTF-8 -*-

# the email addresses are all fake data

member_data = (
    ('limi', 'Alexander Limi', 'bib-demo', 'limi@plone.org'),
    ('runyan', 'Alan Runyan', 'bib-demo', 'runyan@plone.org'),
    ('andersen', 'Vidar Andersen', 'bib-demo', 'andersen@plone.org'),
    ('everitt', 'Paul Everitt', 'bib-demo', 'everitt@plone.org'),
    ('tesdal', 'Helge Tesdal', 'bib-demo', 'tesdal@plone.org'),
    ('mckay', 'Andy McKay', 'bib-demo', 'mckay@plone.org'),
    ('pelletier', 'Michel Pelletier', 'bib-demo', 'pelletier@plone.org'),
    ('ritz', 'Raphael Ritz', 'bib-demo', 'ritz@plone.org'),
    ('convent', 'David Convent', 'bib-demo', 'convent@plone.org'),
    ('foerster', 'Thomas Förster', 'bib-demo', 'foerster@plone.org'),
##     ('', '', 'bib-demo', '@plone.org'),
    )

import sys
from os import path
import urllib

# a shortcut
encode = urllib.urlencode

protocol = "http://"

# get the user credentials
# Note: For safty reasons I recommend to generate
# a temporary account with management priviledges
# for exploring this script because basic http
# authentication is used which can easily be sniffed.

## print "\nusername (needs to have the 'Manager' role): ",
## user = sys.stdin.readline()[:-1]
## print "password: ",
## passwd = sys.stdin.readline()[:-1]
## admin = "%s:%s@" % (user, passwd)

print "servername (default: 'localhost'): ",
s_name = sys.stdin.readline()[:-1]
if s_name: server_name = s_name
else: server_name = "localhost"

print "port (default: '8080'): ",
p_name = sys.stdin.readline()[:-1]
if p_name: port = ':' + p_name
else: port = ":8080"

print "site id (default: 'bib-demo'): ",
site_id = sys.stdin.readline()[:-1]
if site_id: site_path = '/' + site_id
else: site_path = "/bib-demo"

server = protocol + server_name + port
site = server + site_path
## admin_at_server = protocol + admin + server_name + port
## admin_at_site = admin_at_server + site_path


# By in- and outcommenting the following
# lines you control the interactivity, the
# logging mode, and whether we make a CMFDefault
# or Plone site.

interactive = 0   # no questions asked
# interactive = 1   # waits after every call

## Plone = 0         # a CMFDefault site
Plone = 1         # a Plone site

#log_mode = 0  # no logs
log_mode = 1  # print to stdout
#log_mode = 2  # write to file


# some utility methods

def log_it(url, params=None, comment=''):
    if not log_mode: return None
    else:
        output = "Calling " + url + '\n'
        if params: output += "with parameters " + params + '\n'
        if comment: output += '\n' + comment + '\n\n'

    if log_mode == 1:
        print output
    else:
        logFile.write(output)

def call(url, params=None, comment=''):
    urllib.urlopen(url,params)
    log_it(url, params, comment)
    if interactive:
        print "\nPress 'Return' to continue."
        sys.stdin.readline()


##
##  Now, we are ready to go :-)
##


# Add our members:

constructor = "/register"

for member_id, fullname, password, email in member_data:

    input = encode({
        'fullname': fullname,
        'username': member_id,
        'password': password,
        'password_confirm': password,
        'email': email
        })

    comment = "register '%s'." % fullname

    call(site + constructor, input, comment)

    # Note that this is called anonymously.

# create member areas

constructor = "/portal_membership/createMemberarea"

for member_id, fullname, password, email in member_data:

    member_at_site = protocol + member_id + ':' + password + '@' \
                     + server_name + port + site_path

    input = encode({
        'member_id': member_id,
        })

    comment = "creating member area for '%s'." % fullname

    call(member_at_site + constructor, input, comment)

