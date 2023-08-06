from __future__ import print_function

import ConfigParser
from optparse import OptionParser
import re
import sys
import urllib2
import warnings

ASSIGNMENTS = re.compile("(?<=li\>)[\S\s]*?(?=\<\/li\>)")
ROLE_NAME = re.compile("Package Index ([a-zA-Z]*)")
IGNORED_NAMES = set(['Package','Index','span','strong','li'])
COMMA_SEP_NAMES = re.compile("(([a-zA-Z]+),?)+?")

def get_server_connection(repository=None):
    if repository is None:
        repository = "http://pypi.python.org/pypi"
    return lambda path, version: urllib2.urlopen("%s/%s/%s" % (repository, path, version)).read()

def get_users_for_package(connection, package, version=''):
    package_page = connection(package, version)
    if "Index of Packages" in package_page:
        warnings.warn("The package %s confused me, patches welcome." % (package), RuntimeWarning)
        raise StopIteration
    assignments = ASSIGNMENTS.findall(package_page)
    for assignment in assignments:
        role = ROLE_NAME.findall(assignment)
        if not role:
            continue
        else:
            role = role[0]
        users = set(a[1] for a in COMMA_SEP_NAMES.findall(assignment)
                    if a[1] not in IGNORED_NAMES|set((role,)))
        yield {'role':role,'users':users}

def print_assignments(connection, package, version=''):
    for assignment in get_users_for_package(connection, package, version):
        print(assignment['role'])
        print('=' * len(assignment['role']))
        print()
        for user in assignment['users']:
            print("\t%s" % user)
        print()

def count_assignments(connection, package, version=''):
    total = 0
    users = set()
    for assignment in get_users_for_package(connection, package, version):
        users |= assignment['users']
    return len(users)

def commandline():
    parser = OptionParser("parker packagename.  You may only omit packagename if supplying a versions config file.")
    parser.add_option("-f", "--factor", dest="factor", action="store", 
                      type="int", metavar="2",
                      help="the minimum bus factor required to prevent an error")
    parser.add_option("-r", "--repository", action="store", type="int",
                      metavar="repository-url",
                      dest="repository", help="The repository to scrape")
    parser.add_option("-c", "--versions-cfg", action="store", type="string",
                      metavar='versions.cfg', dest="versionscfg", 
                      help="A zc.buildout versions section to parse for package names")
    parser.add_option("-v", action="count", dest="verbosity", 
                      help="Increase verbosity by one verbosity unit")
    (options, args) = parser.parse_args()
    
    conn = get_server_connection(options.repository)
    
    if options.factor is None:
        options.factor = 2
    
    if options.verbosity >= 5:
        print("""
    A sophistical rhetorician, inebriated with the exuberance of his own 
    verbosity, and gifted with an egotistical imagination that can at all 
    times command an interminable and inconsistent series of arguments to 
    malign an opponent and to glorify himself. 
        - Benjamin Disraeli, 1st Earl of Beaconsfield
    
    """)
    
    if options.versionscfg is None and not args:
        print("You must supply a package name or versions.cfg")
        sys.exit(1)
    
    if options.versionscfg:
        parse = ConfigParser.ConfigParser()
        parse.optionxform = str
        parse.read(options.versionscfg)
        packages = set("%s==%s" % (a[0],a[1]) for a in parse.items("versions"))
    else:
        packages = set(args)
    
    for package in packages:
        try:
            package, version = package.split("==")
        except ValueError:
            version = ''
        
        try:
            users = count_assignments(conn, package, version)
        except urllib2.HTTPError:
            print("Could not find %s" % (package))
            continue
        if users < options.factor:
            if options.verbosity >= 2:
                print()
                print("*"*40)
                print("The package %s has %d named maintainer(s), which is too few." % (package, users))
                print_assignments(conn, package, version)
                print("*"*40)
                print()
            else:
                roles = get_users_for_package(conn, package, version)
                owners = list(list(roles)[0]['users'])
                print("The package %s has %d named maintainer(s), which is too few.  Contact %s to assign more." % (package, users, owners[0]))
        else:
            if options.verbosity >= 1:
                print("The package %s has %d named maintainers" % (package, users))
        
if __name__ == '__main__':
    commandline()