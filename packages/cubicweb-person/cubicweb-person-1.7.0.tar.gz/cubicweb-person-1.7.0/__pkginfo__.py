# pylint: disable-msg=W0622
"""cubicweb-person packaging information"""

modname = 'person'
distname = "cubicweb-%s" % modname

numversion = (1, 7, 0)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
copyright = '''Copyright (c) 2003-2010 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr/ -- mailto:contact@logilab.fr'''

author = "Logilab"
author_email = "contact@logilab.fr"
web = 'http://www.cubicweb.org/project/%s' % distname

short_desc = "person component for the CubicWeb framework"
long_desc = """\
Summary
-------

`person` provides person informations :

- firstname
- surname / lastname
- civility
- arbitrary text description
- a relation to an email address (NB, the `EmailAddress` entity is
  automatically provided by cubicweb).

If the `addressbook` cube is used, persons will also have *phone* and
*postal_address* relations to store more contact information.

There is a special relation called 'primary_email'. A person can be linked to
multiple email addresses (using the 'use_email' relation). The primary email
must be unique. At the creation of the first email, this relation is
automatically added (though you can change it later, of course).

Recommends
----------

- `addressbook` cube


Usage
-----

In addition of basic entity views, this cube provides :

- *VCardPersonView*, displays a person in the VCard file format
   (.. _VCard on wikipedia: http://en.wikipedia.org/wiki/VCard) .

   This view creates a file called `vcard.vcf` which can be open in
   your addressbook application (Kmail, Thunderbird and so on). In
   order to generate this file, you have to access to a specific view
   using an url address with `?vid=vcard` suffix.

   How to personalize the person primary view in order to add a link
   for the vcard ?

   .. sourcecode:: python

     class PersonalizedPersonPrimaryView(PersonPrimaryView):

         def render_entity_attributes(self, entity):
             super(PersonalizedPersonPrimaryView, self).render_entity_attributes(entity)
             self.w(u'<div><a href="%s">export contact as vcard</a></div>'  % entity.absolute_url(vid='vcard'))

    This view will not be selected by default. You have to registered
    this view or add a selector. For more information, please refer to
    XXX in the doc.

- a *civility facet*, this facet (XXX: ref to facet doc) will be shown
  if a view displays a result set of at least two Person entities with
  different civilities.

"""

classifiers = [
    'Environment :: Web Environment',
    'Framework :: CubicWeb',
    'Programming Language :: Python',
    'Programming Language :: JavaScript',
    ]

__depends_cubes__ = {}
__depends__ = {'cubicweb': '>= 3.6.0'}
__use__ = ()
__recommend__ = ('addressbook',)

# packaging ###

from os import listdir
from os.path import join

THIS_CUBE_DIR = join('share', 'cubicweb', 'cubes', 'person')
try:
    data_files = [
        [THIS_CUBE_DIR,
         [fname for fname in listdir('.')
          if fname.endswith('.py') and fname != 'setup.py']],
        [join(THIS_CUBE_DIR, 'data'),
         [join('data', fname) for fname in listdir('data')]],
        [join(THIS_CUBE_DIR, 'i18n'),
         [join('i18n', fname) for fname in listdir('i18n')]],
        [join(THIS_CUBE_DIR, 'migration'),
         [join('migration', fname) for fname in listdir('migration')]],
        ]
except OSError:
    # we are in an installed directory
    pass

cube_eid = 20342
