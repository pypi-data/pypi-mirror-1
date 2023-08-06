Mr. Parker
==========

"With great power comes great responsibility" - Uncle Ben

Bus Factor
----------

At the 2009 Plone Conference the quote "we usually think of buses as things that
kill programmers" was overheard. A few days later, at the sprint, it was noticed
that a few core packages for Plone 4.0 could only be released by one person.
This package is designed to combat this by ensuring that a given package has
more than a certain number of authorised admins on PyPI.

Syntax
------

This creates a console script called ``parker`` as follows:

::

    parker [--factor=2] 
           [--versions-cfg <configfile>] 
           [--repository=http://pypi.python.org/pypi] [packagename(s)]

:--factor: (also -f) This determines the minimum number of people that have access before an error is raised.  The default is 2.
:--versions-cfg: (also -c) If this option is provided a ``zc.buildout`` versions file will be parsed for the package names
:--repository: (also -r) A repository URL that follows the baroque lookup logic assumptions
:packagename(s): Required if --versions-cfg isn't specified.  Contains one or more packages to check, space separated.

Baroque Lookup Logic
--------------------

Unfortunately, the API doesn't allow us to find what users have access to a
package, so we need to screen scrape. We expect HTML of the following format:

::

     <li>
      <strong>Package Index Owner:</strong>
      <span>deo, smcmahon, MatthewWilkes</span>
     </li>

     <li>
      <strong>Package Index Maintainer:</strong>
      <span>JoeBob</span>
     </li>

That is, a list element that contains Package Index <rolename>: and a comma
separated list, once the tags have been removed.

First, the li tags are extracted

::

    (?<=li\>)[\S\s]*?(?=\<\/li\>)

Then, the role name is extracted:

::

    "Package Index ([a-zA-Z]*)"

and the names are found with:

::

    set(a[0] for a in re.compile("([a-zA-Z]+,?)+?").findall(li) 
             if a[0] not in ['Package','Index',rolename,'span','strong'])

Yes, it is ugly. I know. I wish there was an API for this, or that the markup
was easily scrape-able. For now, this will do.
