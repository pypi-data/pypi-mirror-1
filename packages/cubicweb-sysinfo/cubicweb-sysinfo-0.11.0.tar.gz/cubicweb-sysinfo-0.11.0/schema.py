"""jpl application'schema

:organization: Logilab
:copyright: 2003-2008 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from yams.buildobjs import (EntityType, RelationDefinition, SubjectRelation,
                            String, Date, Int)

try:
    from cubes.file.schema import File, Image
    from cubes.link.schema import Link
except (ImportError, NameError):
    # old-style yams schema will raise NameError on EntityType, RelationType, etc.
    File = import_erschema('File')
    Image = import_erschema('Image')
    Link = import_erschema('Link')

_ = unicode

PERMISSIONS = {'read':   ('managers', 'staff', 'users', 'guests',),
               'add':    ('managers', 'staff', ),
               'update': ('managers', 'staff', 'owners',),
               'delete': ('managers', 'staff', 'owners'),
               }

File.__permissions__ = PERMISSIONS
Image.__permissions__ = PERMISSIONS
Link.__permissions__ = PERMISSIONS

class Part(EntityType):
    name     = String(required=True, fulltextindexed=True, unique=False,
                      maxsize=64, description=_('Name, short description of the part')
                      )

    serial  = String(required=False, fulltextindexed=True, unique=False,
                     maxsize=128, description=_('Part serial number')
                     )

    description = String(fulltextindexed=True,
                         description=_('Detailed description of the part'))

#     part_type = ObjectRelation('PartType', cardinality='11')
    concerned_by = SubjectRelation('File', cardinality='?*')

    situated_in = SubjectRelation('Zone', cardinality='?*')

    warranty_expires = Date(description=_('End of waranty'))


class Device(EntityType):
    name     = String(required=True, fulltextindexed=True, unique=False,
                      maxsize=64, description=_('Name, short description of the device')
                      )

    serial  = String(required=False, fulltextindexed=True, unique=False,
                     maxsize=128, description=_('Device serial number')
                     )

    klass = String(vocabulary=('server',
                               'desktop',
                               'thinclient',
                               'laptop',
                               'display',
                               'printer',
                               'switch',
                               'other',
                               ),
                   description=_('Indicates the general class of this device'))


    description = String(fulltextindexed=True,
                         description=_('Detailed description of the device'))

    made_of = SubjectRelation('Part', cardinality='1*')

    concerned_by = SubjectRelation('File', cardinality='**')

    situated_in = SubjectRelation('Zone', cardinality='?*')

    warranty_expires = Date(description=_('End of waranty'))

# class PartType(EntityType):
#     name     = String(required=True, fulltextindexed=True, unique=False,
#                       maxsize=64,
#                       description=_('Name, short description of the device'))


# the follwing relations still need to be described in this file
# Comment comments File

class Host(EntityType):
    fqdn = String(required=True, fulltextindexed=True, unique=True,
                  maxsize=255,
                  description=_("Fully qualified domain name of this host"))

    ip_addr = String(required=True, fulltextindexed=True, unique=True,
                     maxsize=255, description=_("IP address"))

    hosted_by = SubjectRelation( ('Device', 'Host'), cardinality='1*' )

    os = String(required=True)

class NetworkService(EntityType):
    """Network service as in /etc/services"""
    name = String(required=True, description=_('Service name'))
    port = Int(required=True, description=_('Service port'))
    type = String(required=True, vocabulary=('tcp','udp'), description=_('port type'))

class Application(EntityType):
    """Description of a network application"""
    title = String(required=True,
                   maxsize=255,
                   description=_('Application title'), unique=True)
    description = String(description=_("Application description"))

    has_instance = SubjectRelation( 'Service', cardinality='*1', composite='subject')

class Service(EntityType):
    """An entity describing a service of an IT infrastructure"""

    name = String(required=True, fulltextindexed=True, unique=True,
                  description=_("Service identifier"),
                  maxsize=255,
                  )


    description = String(required=True, fulltextindexed=True,
                         description=_("Detailled description"))


    purpose = String(required=True, vocabulary=('prod', 'dev', 'test', 'deprecated'),
                     description=_('Indicates the intended purpose of this service'))





class comments(RelationDefinition):
    subject = 'Comment'
    object = ('File', 'VersionedFile', 'Service', 'Device', 'Part')


class tags(RelationDefinition):
    subject = 'Tag'
    object = ('File',
              'Image',
              'Link',
              'VersionedFile')

class has_entrypoint(RelationDefinition):
    subject = 'Service'
    object = ('Link',)

class hosted_by(RelationDefinition):
    subject = 'Service'
    object = ('Host',)


class admin_doc(RelationDefinition):
    subject = ('VersionedFile',)
    object = ('Application', 'Service')
    cardinality = '*?'

class user_doc(RelationDefinition):
    subject = ('VersionedFile',
               'Link'
               )
    object = ('Application', 'Service')
    cardinality = '*?'
