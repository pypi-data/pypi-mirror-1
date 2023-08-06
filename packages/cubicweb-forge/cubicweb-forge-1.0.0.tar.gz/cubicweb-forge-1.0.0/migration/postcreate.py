"""forge post creation script, set application's workflows

:organization: Logilab
:copyright: 2003-2008 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubes.forge.schemaperms import xperm

# Ticket workflow

open       = add_state(_('open'),               'Ticket', initial=True)
confirmed  = add_state(_('confirmed'),          'Ticket')
waiting    = add_state(_('waiting feedback'),   'Ticket')
rejected   = add_state(_('rejected'),           'Ticket')
inprogress = add_state(_('in-progress'),        'Ticket')
vp         = add_state(_('validation pending'), 'Ticket')
resolved   = add_state(_('resolved'),           'Ticket')
deprecated = add_state(_('deprecated'),         'Ticket')

add_transition(_('confirm'),   'Ticket', (open,),                       confirmed,
               ('managers', 'staff'), xperm('developer'))
add_transition(_('start'),     'Ticket', (open, confirmed),             inprogress,
               ('managers', 'staff'), xperm('developer'))
add_transition(_('stop'),      'Ticket', (inprogress,),                 confirmed,
               ('managers', 'staff'), xperm('developer'))
add_transition(_('reject'),    'Ticket', (open, confirmed, inprogress), rejected,
               ('managers', 'staff'), xperm('developer'))
add_transition(_('done'),      'Ticket', (open, confirmed, inprogress), vp,
               ('managers', 'staff'), xperm('developer'))
add_transition(_('deprecate'), 'Ticket', (open, confirmed),             deprecated,
               ('managers', 'staff'), xperm('client', 'developer'))
add_transition(_('resolve'),   'Ticket', (vp,),                         resolved,
               ('managers', 'staff'), xperm('client'))
add_transition(_('reopen'),    'Ticket', (vp, rejected),                open,
               ('managers', 'staff'), xperm('client'))
add_transition(_('wait for feedback'),   'Ticket', (open,),             waiting,
               ('managers', 'staff'), xperm('developer'))
add_transition(_('got feedback'),   'Ticket', (waiting,),               open,
               ('managers', 'staff'), xperm('developer'))

checkpoint()


# Version workflow
planned   = add_state(_('planned'),   'Version', initial=True)
dev       = add_state(_('dev'),       'Version')
ready     = add_state(_('ready'),     'Version')
published = add_state(_('published'), 'Version')

add_transition(_('start development'), 'Version', (planned,),   dev,
               ('managers', 'staff'), xperm('developer'))
add_transition(_('ready'),             'Version', (dev,),       ready,
               ('managers', 'staff'), xperm('developer'))
add_transition(_('publish'),           'Version', (dev, ready), published,
               ('managers', 'staff'), xperm('developer'))
add_transition(_('stop development'),  'Version', (dev,),       planned,
               ('managers', 'staff'), xperm('developer'))

checkpoint()


# Project workflow
active = add_state(_('active development'), 'Project', initial=True)
asleep = add_state(_('asleep'),             'Project')
dead   = add_state(_('no more maintained'), 'Project')
moved  = add_state(_('moved'),              'Project')

add_transition(_('temporarily stop development'), 'Project', (active,),        asleep,
               ('managers', 'staff'), 'U has_update_permission X')
add_transition(_('stop maintainance'),            'Project', (active, asleep), dead,
               ('managers', 'staff'), 'U has_update_permission X')
add_transition(_('restart development'),          'Project', (asleep, dead),   active,
               ('managers', 'staff'), 'U has_update_permission X')
add_transition(_('project moved'),                'Project', (active, asleep), moved,
               ('managers', 'staff'), 'U has_update_permission X')

checkpoint()

# TestInstance workflow
todo = add_state(_('todo'),       'TestInstance', initial=True)
succeed = add_state(_('succeed'), 'TestInstance')
failed = add_state(_('failed'),   'TestInstance')

add_transition(_('success'), 'TestInstance', (todo,), succeed,
               ('managers', 'staff'), xperm('client', 'developer'))
add_transition(_('failure'), 'TestInstance', (todo,), failed,
               ('managers', 'staff'), xperm('client', 'developer'))

checkpoint()


# try to find some licenses with devtools
try:
    from logilab.devtools.lib.pkginfo import get_known_licenses, TEMPLATE_DIR
    import codecs
    import os, os.path as osp
    licenses_dir = osp.join(TEMPLATE_DIR, 'licenses')
    for license_name in get_known_licenses():
        shortdesc_filename = osp.join(licenses_dir, '%s.txt' % license_name)
        longdesc_filename = osp.join(licenses_dir, 'full_%s.txt' % license_name)
        args = {'name' : unicode(license_name)}
        try:
            args['short_desc'] = codecs.open(shortdesc_filename, encoding='iso-8859-1').read()
            args['long_desc'] = codecs.open(longdesc_filename, encoding='iso-8859-1').read()
        except IOError:
            args['short_desc'] = u''
            args['long_desc'] = u''
        rql('INSERT License L: L name %(name)s, L shortdesc %(short_desc)s, L longdesc %(long_desc)s', args)
except ImportError:
    import sys
    print >> sys.stderr, "I was unable to import devtools, You will have to create " \
          "licenses entities yourself"
