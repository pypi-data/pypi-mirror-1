"""Definition of the translatefolder content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata
from Products.Archetypes.public import DisplayList

from wwp.translate import translateMessageFactory as _
from wwp.translate.interfaces import Itranslatefolder
from wwp.translate.config import PROJECTNAME

languages_list = DisplayList((  
    ('af','AFRIKAANS'),
    ('sq','ALBANIAN'),
    ('am','AMHARIC'),
    ('ar','ARABIC'),
    ('hy','ARMENIAN'),
    ('az','AZERBAIJANI'),
    ('eu','BASQUE'),
    ('be','BELARUSIAN'),
    ('bn','BENGALI'),
    ('bh','BIHARI'),
    ('bg','BULGARIAN'),
    ('my','BURMESE'),
    ('ca','CATALAN'),
    ('chr','CHEROKEE'),
    ('zh','CHINESE'),
    ('zh-CN','CHINESE_SIMPLIFIED'),
    ('zh-TW','CHINESE_TRADITIONAL'),
    ('hr','CROATIAN'),
    ('cs','CZECH'),
    ('da','DANISH'),
    ('dv','DHIVEHI'),
    ('nl','DUTCH'),
    ('en','ENGLISH'),
    ('eo','ESPERANTO'),
    ('et','ESTONIAN'),
    ('tl','FILIPINO'),
    ('fi','FINNISH'),
    ('fr','FRENCH'),
    ('gl','GALICIAN'),
    ('ka','GEORGIAN'),
    ('de','GERMAN'),
    ('el','GREEK'),
    ('gn','GUARANI'),
    ('gu','GUJARATI'),
    ('iw','HEBREW'),
    ('hi','HINDI'),
    ('hu','HUNGARIAN'),
    ('is','ICELANDIC'),
    ('id','INDONESIAN'),
    ('iu','INUKTITUT'),
    ('it','ITALIAN'),
    ('ja','JAPANESE'),
    ('kn','KANNADA'),
    ('kk','KAZAKH'),
    ('km','KHMER'),
    ('ko','KOREAN'),
    ('ku','KURDISH'),
    ('ky','KYRGYZ'),
    ('lo','LAOTHIAN'),
    ('lv','LATVIAN'),
    ('lt','LITHUANIAN'),
    ('mk','MACEDONIAN'),
    ('ms','MALAY'),
    ('ml','MALAYALAM'),
    ('mt','MALTESE'),
    ('mr','MARATHI'),
    ('mn','MONGOLIAN'),
    ('ne','NEPALI'),
    ('no','NORWEGIAN'),
    ('or','ORIYA'),
    ('ps','PASHTO'),
    ('fa','PERSIAN'),
    ('pl','POLISH'),
    ('pt-PT','PORTUGUESE'),
    ('pa','PUNJABI'),
    ('ro','ROMANIAN'),
    ('ru','RUSSIAN'),
    ('sa','SANSKRIT'),
    ('sr','SERBIAN'),
    ('sd','SINDHI'),
    ('si','SINHALESE'),
    ('sk','SLOVAK'),
    ('sl','SLOVENIAN'),
    ('es','SPANISH'),
    ('sw','SWAHILI'),
    ('sv','SWEDISH'),
    ('tg','TAJIK'),
    ('ta','TAMIL'),
    ('tl','TAGALOG'),
    ('te','TELUGU'),
    ('th','THAI'),
    ('bo','TIBETAN'),
    ('tr','TURKISH'),
    ('uk','UKRAINIAN'),
    ('ur','URDU'),
    ('uz','UZBEK'),
    ('ug','UIGHUR'),
    ('vi','VIETNAMESE'),
    ('','UNKNOWN'),
))


translatefolderSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-


))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

translatefolderSchema['title'].storage = atapi.AnnotationStorage()
translatefolderSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    translatefolderSchema,
    folderish=True,
    moveDiscussion=False
)

class translatefolder(folder.ATFolder):
    """language folder containing translator items"""
    implements(Itranslatefolder)

    meta_type = "translatefolder"
    schema = translatefolderSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-



atapi.registerType(translatefolder, PROJECTNAME)
