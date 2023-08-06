"""forge application'schema

Security groups :
* managers (eg site admins)
* users (every authenticated users)
* guests (anonymous users)
* staff (subset of users)

Local permission (granted by project):
* developer
  * XXX describe
* client:
  * add version
  * add ticket
  * add/remove tickets from version in the 'planned' state
  * add/delete test cards
  * add documentation file, screenshots, ticket's attachment

:organization: Logilab
:copyright: 2003-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubicweb.schema import format_constraint
from cubes.forge.schemaperms import (sexpr, oexpr, xexpr, xrexpr, xorexpr,
                                     restricted_oexpr, xperm)


class Project(EntityType):
    """a project is a logical group of tasks/information which produce a final value. That
    may be a software or documentation project, a web site or whatever.
    """
    permissions = {
        'read':   ('managers', 'users', 'guests',),
        'add':    ('managers', 'staff',),
        'update': ('managers', 'staff', 'owners',),
        'delete': ('managers', 'owners'),
        }

    ## attributes
    name      = String(required=True, fulltextindexed=True, unique=True,
                       constraints=[SizeConstraint(32)])
    summary   = String(fulltextindexed=True,
                       constraints=[SizeConstraint(128)],
                       description=_('one line description of the project'))

    description_format = String(meta=True, internationalizable=True,
                                default='text/rest', constraints=[format_constraint])
    description = String(fulltextindexed=True,
                         description=_('more detailed description'))

    homepage  = String(maxsize=128, description=_('url to project\'s home page. Leave this field '
                                                  'empty if the project is fully heberged here.'))
    vcsurl    = String(maxsize=256, description=_('url to access to the project\'s version control system'))
    reporturl = String(maxsize=256, description=_('url to access to the project\'s automatic test reports'))
    downloadurl = String(constraints=[SizeConstraint(256)],
                         description=_('url to access tarball for releases of the project'))

    ## relations
    uses = SubjectRelation('Project',
                           constraints=[RQLVocabularyConstraint('S in_state ST, ST name "active development"')],
                           description=_('project\'s dependencies'))
    recommends = SubjectRelation('Project',
                                 description=_('project\'s optional dependencies'))

    in_state = SubjectRelation('State', cardinality='1*',
                               constraints=[RQLConstraint('O state_of ET, S is ET')],
                               description=_('development status'))
    wf_info_for = ObjectRelation('TrInfo', cardinality='1*', composite='object')

    interested_in = ObjectRelation('CWUser',
                                   description=_('users which want to be notified for this project\'s events'))

    documented_by = SubjectRelation(('Card', 'File'),
                                    constraints=[RQLVocabularyConstraint('S in_state ST, ST name "active development"')],
                                    description=_('project\'s documentation'))

    screenshot = SubjectRelation('Image',
                                 constraints=[RQLVocabularyConstraint('S in_state ST, ST name "active development"')],
                                 description=_('project\'s screenshot'))

    mailinglist_of = ObjectRelation('MailingList', cardinality='*?',
                                    description=_("Project's related mailing list"))


class uses(RelationType):
    permissions = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers', RRQLExpression('U has_update_permission S', 'S'),),
        'delete': ('managers', RRQLExpression('U has_update_permission S', 'S'),),
        }

class recommends(RelationType):
    permissions = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers', RRQLExpression('U has_update_permission S', 'S'),),
        'delete': ('managers', RRQLExpression('U has_update_permission S', 'S'),),
        }


class ExtProject(EntityType):
    """project developed externally of the cubicweb forge application"""
    permissions = {
        'read':   ('managers', 'users', 'guests',),
        'add':    ('managers', 'staff',),
        'update': ('managers', 'staff', 'owners',),
        'delete': ('managers', 'owners'),
        }

    name = String(required=True, fulltextindexed=True, unique=True,
                  constraints=[SizeConstraint(32)])
    description_format = String(meta=True, internationalizable=True,
                                default='text/rest', constraints=[format_constraint])
    description = String(fulltextindexed=True, constraints=[SizeConstraint(512)])
    homepage  = String(maxsize=128, description=_('url to project\'s home page.'))


class Version(EntityType):
    """a version is defining the content of a particular project's release"""

    permissions = {
        'read':   ('managers', 'users', 'guests',),
        # right to add Version is actually granted on the version_of relation
        'add':    ('managers', 'users'),
        'update': ('managers', 'staff', 'owners',),
        'delete': ('managers', ),
        }

    ## attributes
    num              = String(required=True, fulltextindexed=True, indexed=True,
                              constraints=[SizeConstraint(16)],
                              description=_('release number'))
    description_format = String(meta=True, internationalizable=True,
                                default='text/rest', constraints=[format_constraint])
    description      = String(fulltextindexed=True,
                              description=_('targets for this version'))
    starting_date   = Date(description=_('estimated starting date'))
    prevision_date   = Date(description=_('estimated publication date'))
    publication_date = Date(description=_('actual publication date'))

    ## relations
    version_of = SubjectRelation('Project', cardinality='1*', composite='object',
                                 constraints=[RQLVocabularyConstraint('O in_state ST, ST name "active development"')])
    todo_by = SubjectRelation('CWUser',
                              constraints=[RQLConstraint('O in_state ST, ST name "activated"')],
                              description=_('users responsible for this version'))
    in_state = SubjectRelation('State', cardinality='1*',
                               constraints=[RQLConstraint('O state_of ET, S is ET')],
                               description=_('development status'))
    wf_info_for = ObjectRelation('TrInfo', cardinality='1*', composite='object')

    conflicts = SubjectRelation('Version',
                                constraints=[RQLVocabularyConstraint('S version_of PS, O version_of PO, PS uses PO')],
                                description=_('client project\'s version conflicting with this version'))
    depends_on = SubjectRelation('Version',
                                 constraints=[RQLVocabularyConstraint('S version_of PS, O version_of PO, PS uses PO')],
                                 description=_('client project\'s version dependency for this version'))


class Ticket(EntityType):
    """a ticket is representing some kind of work to do (or done) on a project
    (bug fix, feature request...)
    """
    permissions = {
        'read':   ('managers', 'users', 'guests',),
        # right to add Ticket is actually granted on the concerns relation
        'add':    ('managers', 'users',),
        # client can only modify tickets when they are in the "open" state
        'update': ('managers', 'staff', xexpr('developer'),
                   ERQLExpression(xperm('client')+', X in_state S, S name "open"'),),
        'delete': ('managers', ),
        }

    ## attributes
    title = String(required=True, fulltextindexed=True,
                   constraints=[SizeConstraint(128)])
    type = String(required=True, internationalizable=True,
                  constraints=[StaticVocabularyConstraint(
        (_('bug'), _('story')))],
                  description=_("ticket's type"), default='bug')
    priority = String(required=True, internationalizable=True,
                      constraints=[StaticVocabularyConstraint(
        (_('important'), _('normal'), _('minor')))],
                      description=_("importance"), default='normal')
    load = Float(description=_('load for this ticket in day.man'))
    load_left = Float(description=_('remaining load for this ticket in day.man'))

    description_format = String(meta=True, internationalizable=True,
                                default='text/rest', constraints=[format_constraint])
    description = String(fulltextindexed=True,
                         description=_("give any useful information (to "
                                       "describe a bug think to give your "
                                       "configuration and some way to reproduce"
                                       " it whenever possible)"))

    ## relations
    concerns = SubjectRelation('Project', cardinality='1*', composite='object',
                               constraints=[RQLVocabularyConstraint('O in_state ST, ST name "active development"')])
    appeared_in = SubjectRelation(('Version'), cardinality='?*',
                                   constraints=[RQLConstraint('S concerns P, O version_of P'),
                                                RQLVocabularyConstraint('O in_state ST, ST name "published"')],
                                   description=_("version in which a bug has been encountered"))
    done_in = SubjectRelation(('Version'), cardinality='?*',
                              constraints=[RQLConstraint('S concerns P, O version_of P'),
                                           RQLVocabularyConstraint('O in_state ST, NOT ST name "published"')],
                              description=_("version in which this ticket will be / has been  done"))
    in_state = SubjectRelation('State', cardinality='1*',
                               constraints=[RQLConstraint('O state_of ET, S is ET')])
    wf_info_for = ObjectRelation('TrInfo', cardinality='1*', composite='object')

    attachment = SubjectRelation(('File', 'Image'),
                                 description=_('files related to this ticket (screenshot, file needed to reproduce a bug...)'))

    identical_to = SubjectRelation('Ticket',
                                   constraints=[RQLConstraint('S concerns P, O concerns P')])
    depends_on = SubjectRelation('Ticket',
                                 description=_("ticket which has to be done to complete this one"),
                                 constraints=[RQLVocabularyConstraint('S concerns P, EXISTS(O concerns P) '
                                                                      'OR EXISTS(O concerns P2, P uses P2)')])

    comments = ObjectRelation('Comment', cardinality='1*', composite='object')


class License(EntityType):
    permissions = {
        'read':   ('managers', 'users', 'guests',),
        'add':    ('managers', ),
        'update': ('managers', 'owners',),
        'delete': ('managers', 'owners'),
        }
    ## attributes
    name  = String(required=True, fulltextindexed=True, unique=True,
                   constraints=[SizeConstraint(64)])
    # XXX shortesc is actually licence's disclaimer
    shortdesc = String(required=False, fulltextindexed=True, description=_('disclaimer of the license'))
    longdesc_format = String(meta=True, internationalizable=True,
                             default='text/plain', constraints=[format_constraint])
    longdesc = String(required=False, fulltextindexed=True, description=_("full license's text"))
    url = String(maxsize=256)
    ## relations
    license_of = SubjectRelation('Project', cardinality='**',
                                 description=_("Project's license"))


class TestInstance(EntityType):
    permissions = {
        'read':   ('managers', 'users', 'guests'),
        'add':    (), # handled by hook
        'update': ('managers',),
        'delete': ('managers', xexpr('client')),
        }
    ## attributes
    # name size constraint should be the same as Card's title
    name  = String(required=True, fulltextindexed=True, constraints=[SizeConstraint(256)])
    ## relations
    instance_of = SubjectRelation('Card', cardinality='1*', composite='object')
    for_version = SubjectRelation('Version', cardinality='1*', composite='object')
    generate_bug = SubjectRelation('Ticket', description=_('link to a bug encountered while passing the test'))
    in_state = SubjectRelation('State', cardinality='1*',
                               constraints=[RQLConstraint('O state_of ET, X is ET')])
    wf_info_for = ObjectRelation('TrInfo', cardinality='1*', composite='object')
    comments = ObjectRelation('Comment', cardinality='1*', composite='object')

class test_case_of(RelationType):
    """specify that a card is describing a test for a project"""
    subject = 'Card'
    object = 'Project'
    cardinality = '?*'
    permissions = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers', 'staff', oexpr('developer', 'client'),),
        'delete': ('managers', 'staff', oexpr('developer', 'client'),),
        }

class test_case_for(RelationType):
    """specify that a card is describing a test for a particular story"""
    subject = 'Card'
    object = 'Ticket'
    cardinality = '?*'
    permissions = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers', 'staff', oexpr('developer', 'client'),),
        'delete': ('managers', 'staff', oexpr('developer', 'client'),),
        }


File = import_erschema('File')
File.permissions = {
    'read':   ('managers', 'users', 'guests'),
    'add':    ('managers', 'staff',
               ERQLExpression('Y attachment X, Y is Email, U has_update_permission Y'),
               xorexpr('attachment', 'File', 'developer', 'client'),
               xorexpr('documented_by', 'File', 'developer', 'client'),),
    'update': ('managers', 'staff', 'owners',),
    'delete': ('managers', 'owners'),
    }


Image = import_erschema('Image')
Image.permissions = {
    'read':   ('managers', 'users', 'guests'),
    'add':    ('managers', 'staff',
               xorexpr('attachment', 'Image', 'developer', 'client'),
               xorexpr('screenshot', 'Image', 'developer', 'client'),),
    'update': ('managers', 'staff', 'owners',),
    'delete': ('managers', 'owners'),
    }

Card = import_erschema('Card')
Card.permissions = {
    'read':   ('managers', 'users', 'guests'),
    'add':    ('managers', 'staff',
               xorexpr('documented_by', 'Card', 'developer', 'client'),
               xrexpr('test_case_for', 'developer', 'client'),
               xrexpr('test_case_of', 'developer', 'client'),),
    'update': ('managers', 'staff', 'owners',),
    'delete': ('managers', 'owners'),
    }

# extra relation definitions ##################################################

class see_also(RelationDefinition):
    symetric = True
    subject = ('ExtProject', 'Project', 'Ticket', 'Card', 'File', 'Image',
               'Email')
    object = ('ExtProject', 'Project', 'Ticket', 'Card', 'File', 'Image',
              'Email')

class missing_comments(RelationDefinition):
    subject = 'Comment'
    name = 'comments'
    object = ('Card', 'File', 'Image', 'Email')
    cardinality = '1*'
    composite = 'object'


class missing_tags(RelationDefinition):
    name = 'tags'
    subject = 'Tag'
    object = ('ExtProject', 'Project', 'Version', 'Ticket',
              'License', 'MailingList',
              'Card', 'File', 'Image', 'Email')

class missing_filed_under(RelationDefinition):
    name = 'filed_under'
    subject = ('ExtProject', 'Project', 'Card', 'File')
    object = 'Folder'

class missing_require_permission(RelationDefinition):
    name = 'require_permission'
    subject = ('ExtProject', 'Project', 'Version', 'Ticket', 'TestInstance',
               'Comment', 'Image', 'File', 'Card')
    object = 'CWPermission'

class has_group_permission(RelationDefinition):
    """short cut relation for 'U in_group G, P require_group G' for efficiency
    reason. This relation is set automatically, you should not set this.
    """
    subject = 'CWUser'
    object = 'CWPermission'
    permissions = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers',),
        'delete': ('managers',),
        }

# relation types permissions ##################################################

class license_of(RelationType):
    permissions = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers', RRQLExpression('U has_update_permission O', 'O'),),
        'delete': ('managers', RRQLExpression('U has_update_permission O', 'O'),),
        }

class mailinglist_of(RelationType):
    permissions = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers', RRQLExpression('U has_update_permission O', 'O'),),
        'delete': ('managers', RRQLExpression('U has_update_permission O', 'O'),),
        }

class documented_by(RelationType):
    permissions = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers', 'staff', sexpr('developer', 'client'),),
        'delete': ('managers', 'staff', sexpr('developer', 'client'),),
    }

class screenshot(RelationType):
    permissions = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers', 'staff', sexpr('developer', 'client'),),
        'delete': ('managers', 'staff', sexpr('developer', 'client'),),
    }


class version_of(RelationType):
    """link a version to its project. A version is necessarily linked to one and
    only one project.
    """
    inlined = True
    permissions = {
        'read':   ('managers', 'users', 'guests',),
        'add':    ('managers', 'staff', oexpr('client'),),
        'delete': ('managers', ),
        }

class todo_by(RelationType):
    permissions = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers',),
        'delete': ('managers',),
        }

class conflicts(RelationType):
    symetric = True
    permissions = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers', 'staff', sexpr('developer'),),
        'delete': ('managers', 'staff', sexpr('developer'),),
        }


class concerns(RelationType):
    """link a ticket to its project. A ticket is necessarily linked to one and
    only one project.
    """
    inlined = True
    permissions = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers', 'staff', oexpr('developer', 'client'),),
        'delete': ('managers', 'staff',),
    }

class done_in(RelationType):
    """link a ticket to the version in which it has been done"""
    inlined = True
    permissions = {
        'read':   ('managers', 'users', 'guests'),
        # XXX should require permission on the ticket or on the version, or both?
        # XXX should check the state of a ticket
        'add':    ('managers', 'staff', restricted_oexpr('O in_state ST, ST name "planned"', 'client'),),
        'delete': ('managers', 'staff', restricted_oexpr('O in_state ST, ST name "planned"', 'client'),),
    }

class appeared_in(RelationType):
    permissions = {
        'read':   ('managers', 'users', 'guests'),
        # XXX should require permission on the ticket or on the version, or both?
        'add':    ('managers', 'staff', sexpr('developer', 'client'),),
        'delete': ('managers', 'staff', sexpr('developer', 'client'),),
    }

class attachment(RelationType):
    permissions = {
        'read':   ('managers', 'users', 'guests'),
        # also used for Email attachment File
        'add':    ('managers', 'staff', RRQLExpression('U has_update_permission S', 'S')),
        'delete': ('managers', 'staff', RRQLExpression('U has_update_permission S', 'S')),
    }

class depends_on(RelationType):
    permissions = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers', 'staff', sexpr('developer', 'client'),),
        'delete': ('managers', 'staff', sexpr('developer', 'client'),),
    }


class for_version(RelationType):
    inlined = True
    permissions = {
        'read':   ('managers', 'users', 'guests'),
        'add':    (), # handled by hook
        'delete': ('managers', 'users',), # will need delete perm on TestInstance
        }

class instance_of(RelationType):
    inlined = True
    permissions = {
        'read':   ('managers', 'users', 'guests'),
        'add':    (), # handled by hook
        'delete': ('managers', 'users',), # will need delete perm on TestInstance
        }

class generate_bug(RelationType):
    permissions = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers', 'staff', sexpr('developer', 'client'),),
        'delete': ('managers', 'staff', sexpr('developer', 'client'),),
    }

