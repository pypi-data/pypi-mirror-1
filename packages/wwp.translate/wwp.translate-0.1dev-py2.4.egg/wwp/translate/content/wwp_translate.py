"""Definition of the wwp_translate content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from Products.Archetypes.public import DisplayList

from wwp.translate import translateMessageFactory as _
from wwp.translate.interfaces import Iwwp_translate
from wwp.translate.config import PROJECTNAME


#languages from google api
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

wwp_translateSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

    atapi.StringField(
        'from_lang',
        vocabulary=languages_list,
        storage=atapi.AnnotationStorage(),
        widget=atapi.SelectionWidget(
            label=_(u"From language"),
            description=_(u"translate from this language"),
            format="select",
        ),
        required=True,
    ),

    atapi.StringField(
        'to_lang',
        vocabulary=languages_list,
        storage=atapi.AnnotationStorage(),
        widget=atapi.SelectionWidget(
            label=_(u"To language"),
            description=_(u"Translate to this language"),
            format="select",
        ),
        required=True,
    ),
    
))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

wwp_translateSchema['title'].storage = atapi.AnnotationStorage()
wwp_translateSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(wwp_translateSchema, moveDiscussion=False)

class wwp_translate(base.ATCTContent):
    """Translation of text to and from different languages"""
    implements(Iwwp_translate)

    
    
    meta_type = "wwp_translate"
    schema = wwp_translateSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-
    to_lang = atapi.ATFieldProperty('to_lang')

    from_lang = atapi.ATFieldProperty('from_lang')
    
    @property
    def is_published(self):        
        #app = context.restrictedTraverse(r.getPath()) # chechout the object
        #check the permission of the object for anonymous user:
        obj_viewed = [x for x in self.permissionsOfRole('Anonymous') if x['name']=='View']
        if obj_viewed[0]['selected'] == 'SELECTED':
            return True
        else:
            return False
        
    def getTo_lang_long(self):
        lang_dict={'': 'Unknown', 'gu': 'Gujarati', 'gn': 'Guarani', 'gl': 'Galician', 'lo': 'Laothian', 'tr': 'Turkish', 'lv': 'Latvian', 'tl': 'Tagalog', 'th': 'Thai', 'tg': 'Tajik', 'te': 'Telugu', 'ta': 'Tamil', 'de': 'German', 'da': 'Danish', 'dv': 'Dhivehi', 'el': 'Greek', 'eo': 'Esperanto', 'en': 'English', 'zh': 'Chinese', 'eu': 'Basque', 'et': 'Estonian', 'es': 'Spanish', 'ru': 'Russian', 'zh-cn': 'Chinese_simplified', 'ro': 'Romanian', 'be': 'Belarusian', 'bg': 'Bulgarian', 'uk': 'Ukrainian', 'bn': 'Bengali', 'bo': 'Tibetan', 'bh': 'Bihari', 'ja': 'Japanese', 'or': 'Oriya', 'ca': 'Catalan', 'cs': 'Czech', 'ps': 'Pashto', 'zh-tw': 'Chinese_traditional', 'lt': 'Lithuanian', 'chr': 'Cherokee', 'pa': 'Punjabi', 'vi': 'Vietnamese', 'pl': 'Polish', 'hy': 'Armenian', 'hr': 'Croatian', 'iu': 'Inuktitut', 'hu': 'Hungarian', 'hi': 'Hindi', 'uz': 'Uzbek', 'pt-pt': 'Portuguese', 'ml': 'Malayalam', 'mn': 'Mongolian', 'mk': 'Macedonian', 'ur': 'Urdu', 'mt': 'Maltese', 'ms': 'Malay', 'mr': 'Marathi', 'ug': 'Uighur', 'my': 'Burmese', 'af': 'Afrikaans', 'ko': 'Korean', 'is': 'Icelandic', 'am': 'Amharic', 'it': 'Italian', 'iw': 'Hebrew', 'kn': 'Kannada', 'ar': 'Arabic', 'az': 'Azerbaijani', 'id': 'Indonesian', 'nl': 'Dutch', 'no': 'Norwegian', 'ne': 'Nepali', 'fr': 'French', 'fa': 'Persian', 'fi': 'Finnish', 'ky': 'Kyrgyz', 'ka': 'Georgian', 'kk': 'Kazakh', 'sr': 'Serbian', 'sq': 'Albanian', 'sw': 'Swahili', 'sv': 'Swedish', 'km': 'Khmer', 'sk': 'Slovak', 'si': 'Sinhalese', 'ku': 'Kurdish', 'sl': 'Slovenian', 'sa': 'Sanskrit', 'sd': 'Sindhi'}
        return lang_dict[str(self.to_lang).lower()]
    
    def getFrom_lang_long(self):
        lang_dict={'': 'Unknown', 'gu': 'Gujarati', 'gn': 'Guarani', 'gl': 'Galician', 'lo': 'Laothian', 'tr': 'Turkish', 'lv': 'Latvian', 'tl': 'Tagalog', 'th': 'Thai', 'tg': 'Tajik', 'te': 'Telugu', 'ta': 'Tamil', 'de': 'German', 'da': 'Danish', 'dv': 'Dhivehi', 'el': 'Greek', 'eo': 'Esperanto', 'en': 'English', 'zh': 'Chinese', 'eu': 'Basque', 'et': 'Estonian', 'es': 'Spanish', 'ru': 'Russian', 'zh-cn': 'Chinese_simplified', 'ro': 'Romanian', 'be': 'Belarusian', 'bg': 'Bulgarian', 'uk': 'Ukrainian', 'bn': 'Bengali', 'bo': 'Tibetan', 'bh': 'Bihari', 'ja': 'Japanese', 'or': 'Oriya', 'ca': 'Catalan', 'cs': 'Czech', 'ps': 'Pashto', 'zh-tw': 'Chinese_traditional', 'lt': 'Lithuanian', 'chr': 'Cherokee', 'pa': 'Punjabi', 'vi': 'Vietnamese', 'pl': 'Polish', 'hy': 'Armenian', 'hr': 'Croatian', 'iu': 'Inuktitut', 'hu': 'Hungarian', 'hi': 'Hindi', 'uz': 'Uzbek', 'pt-pt': 'Portuguese', 'ml': 'Malayalam', 'mn': 'Mongolian', 'mk': 'Macedonian', 'ur': 'Urdu', 'mt': 'Maltese', 'ms': 'Malay', 'mr': 'Marathi', 'ug': 'Uighur', 'my': 'Burmese', 'af': 'Afrikaans', 'ko': 'Korean', 'is': 'Icelandic', 'am': 'Amharic', 'it': 'Italian', 'iw': 'Hebrew', 'kn': 'Kannada', 'ar': 'Arabic', 'az': 'Azerbaijani', 'id': 'Indonesian', 'nl': 'Dutch', 'no': 'Norwegian', 'ne': 'Nepali', 'fr': 'French', 'fa': 'Persian', 'fi': 'Finnish', 'ky': 'Kyrgyz', 'ka': 'Georgian', 'kk': 'Kazakh', 'sr': 'Serbian', 'sq': 'Albanian', 'sw': 'Swahili', 'sv': 'Swedish', 'km': 'Khmer', 'sk': 'Slovak', 'si': 'Sinhalese', 'ku': 'Kurdish', 'sl': 'Slovenian', 'sa': 'Sanskrit', 'sd': 'Sindhi'}
        return lang_dict[str(self.from_lang).lower()]


atapi.registerType(wwp_translate, PROJECTNAME)
