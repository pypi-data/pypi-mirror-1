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
_ = unicode

from yams.buildobjs import (
    EntityType, RelationType, RelationDefinition,
    SubjectRelation, ObjectRelation, String, Float, RichString)

from cubicweb.schema import (
    RQLVocabularyConstraint, RRQLExpression, ERQLExpression,
    WorkflowableEntityType, make_workflowable)
from cubes.tracker.schemaperms import (
    sexpr, oexpr, xexpr, xrexpr, xorexpr, xperm)

try:
    from cubes.tracker.schema import Project, Ticket, Version
    from cubes.file.schema import File, Image
    from cubes.card.schema import Card
except (ImportError, NameError):
    Project = import_erschema('Project')
    Ticket = import_erschema('Ticket')
    Version = import_erschema('Version')
    File = import_erschema('File')
    Image = import_erschema('Image')
    Card = import_erschema('Card')

Project.add_relation(String(maxsize=128,
                            description=_('url to project\'s home page. Leave this field '
                                          'empty if the project is fully hosted here.')),
                     name='homepage')
Project.add_relation(String(maxsize=256,
                            description=_('url to access to the project\'s version control system')),
                     name='vcsurl')
Project.add_relation(String(maxsize=256,
                            description=_('url to access to the project\'s automatic test reports')),
                     name='reporturl')
Project.add_relation(String(maxsize=256,
                            description=_('url to access tarball for releases of the project')),
                     name='downloadurl')
Project.add_relation(SubjectRelation('Project', description=_('project\'s optional dependencies')),
                        name='recommends')
Project.add_relation(SubjectRelation(('Card', 'File'),
                                     constraints=[RQLVocabularyConstraint('S in_state ST, ST name "active development"')],
                                     description=_('project\'s documentation')),
                     name='documented_by')
Project.add_relation(SubjectRelation('Image',
                                    constraints=[RQLVocabularyConstraint('S in_state ST, ST name "active development"')],
                                    description=_('project\'s screenshot')),
                     name='screenshot')
Project.add_relation(ObjectRelation('MailingList', cardinality='*?',
                                    description=_("Project's related mailing list")),
                     name='mailinglist_of')
Project.get_relations('uses').next().constraints = [
    RQLVocabularyConstraint('S in_state ST, ST name "active development"') # XXX same thing for O
    ]
make_workflowable(Project)

class recommends(RelationType):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers', RRQLExpression('U has_update_permission S', 'S'),),
        'delete': ('managers', RRQLExpression('U has_update_permission S', 'S'),),
        }

class ExtProject(EntityType):
    """project developed externally of the cubicweb forge application"""
    __permissions__ = {
        'read':   ('managers', 'users', 'guests',),
        'add':    ('managers', 'staff',),
        'update': ('managers', 'staff', 'owners',),
        'delete': ('managers', 'owners'),
        }

    name = String(required=True, fulltextindexed=True, unique=True, maxsize=32)
    description = RichString(fulltextindexed=True, maxsize=512)
    homepage  = String(maxsize=128, description=_('url to project\'s home page.'))



Ticket.add_relation(Float(description=_('load for this ticket in day.man')),
                    name='load')
Ticket.add_relation(Float(description=_('remaining load for this ticket in day.man')),
                    name='load_left')

Ticket.add_relation(SubjectRelation(('File', 'Image'),
                                 description=_('files related to this ticket (screenshot, file needed to reproduce a bug...)')),
                    name='attachment')
Ticket.add_relation(ObjectRelation('Comment', cardinality='1*', composite='object'),
                    name='comments')
Ticket.get_relations('concerns').next().constraints = [
    RQLVocabularyConstraint('O in_state ST, ST name "active development"')
    ]

# client can only modify tickets when they are in the "open" state
Ticket.__permissions__['update'] = ('managers', 'staff', xexpr('developer'),
                                ERQLExpression(xperm('client')+', X in_state S, S name "open"'))

Version.add_relation(Float(description=_('computed attribute'), default=0), name='progress_target')
Version.add_relation(Float(description=_('computed attribute'), default=0), name='progress_done')
Version.add_relation(Float(description=_('computed attribute'), default=0), name='progress_todo')
Version.get_relations('version_of').next().constraints = [
    RQLVocabularyConstraint('O in_state ST, ST name "active development"')
    ]
Version.get_relations('depends_on').next().constraints[0].restriction += ', EXISTS(PS recommends PO)'
Version.get_relations('conflicts').next().constraints[0].restriction += ', EXISTS(PS recommends PO)'

class License(EntityType):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests',),
        'add':    ('managers', ),
        'update': ('managers', 'owners',),
        'delete': ('managers', 'owners'),
        }
    ## attributes
    name  = String(required=True, fulltextindexed=True, unique=True, maxsize=64)
    # XXX shortesc is actually licence's disclaimer
    shortdesc = String(required=False, fulltextindexed=True, description=_('disclaimer of the license'))
    longdesc = RichString(required=False, fulltextindexed=True, description=_("full license's text"))
    url = String(maxsize=256)
    ## relations
    license_of = SubjectRelation('Project', cardinality='**',
                                 description=_("Project's license"))


File.__permissions__ = {
    'read':   ('managers', 'users', 'guests'),
    'add':    ('managers', 'staff',
               ERQLExpression('Y attachment X, Y is Email, U has_update_permission Y'),
               xorexpr('attachment', 'File', 'developer', 'client'),
               xorexpr('documented_by', 'File', 'developer', 'client'),),
    'update': ('managers', 'staff', 'owners',),
    'delete': ('managers', 'owners'),
    }


Image.__permissions__ = {
    'read':   ('managers', 'users', 'guests'),
    'add':    ('managers', 'staff',
               xorexpr('attachment', 'Image', 'developer', 'client'),
               xorexpr('screenshot', 'Image', 'developer', 'client'),),
    'update': ('managers', 'staff', 'owners',),
    'delete': ('managers', 'owners'),
    }

# XXX should be independant of testcard cube'schema
Card.__permissions__ = {
    'read':   ('managers', 'users', 'guests'),
    'add':    ('managers', 'staff',
               xorexpr('documented_by', 'Card', 'developer', 'client'),
               xrexpr('test_case_for', 'developer', 'client'),
               xrexpr('test_case_of', 'developer', 'client'),),
    'update': ('managers', 'staff', 'owners',),
    'delete': ('managers', 'owners'),
    }

# nosy list configuration ######################################################

class interested_in(RelationDefinition):
    '''users to notify of changes concerning this entity'''
    subject = 'CWUser'
    object = ('Project', 'Ticket')

class nosy_list(RelationDefinition):
    subject = ('Email', 'ExtProject', 'Project', 'Version', 'Ticket',
               'Comment', 'Image', 'File', 'Card', 'TestInstance')
    object = 'CWUser'

# extra relation definitions ##################################################

class see_also(RelationDefinition):
    symmetric = True
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
    subject = ('ExtProject', 'Comment', 'Image', 'File', 'Card')
    object = 'CWPermission'

# relation types permissions ##################################################

class license_of(RelationType):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers', RRQLExpression('U has_update_permission O', 'O'),),
        'delete': ('managers', RRQLExpression('U has_update_permission O', 'O'),),
        }

class mailinglist_of(RelationType):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers', RRQLExpression('U has_update_permission O', 'O'),),
        'delete': ('managers', RRQLExpression('U has_update_permission O', 'O'),),
        }

class documented_by(RelationType):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers', 'staff', sexpr('developer', 'client'),),
        'delete': ('managers', 'staff', sexpr('developer', 'client'),),
    }

class screenshot(RelationType):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        'add':    ('managers', 'staff', sexpr('developer', 'client'),),
        'delete': ('managers', 'staff', sexpr('developer', 'client'),),
    }


class attachment(RelationType):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests'),
        # also used for Email attachment File
        'add':    ('managers', 'staff', RRQLExpression('U has_update_permission S', 'S')),
        'delete': ('managers', 'staff', RRQLExpression('U has_update_permission S', 'S')),
    }
