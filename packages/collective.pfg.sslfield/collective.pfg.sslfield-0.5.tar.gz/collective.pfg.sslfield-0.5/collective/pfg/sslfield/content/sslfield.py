__version__ = '$Id: sslfield.py 60040 2008-03-05 16:06:55Z erral $'

from AccessControl import ClassSecurityInfo

from Products.Archetypes.atapi import *
from Products.ATContentTypes.content.base import registerATCT

from Products.PloneFormGen.content import fieldsBase, fields
from collective.pfg.sslfield.config import *

# DisplayList msgids must be strings, no Unicode, no zope.i18nmessageid instances
# With this horrible hack, I can get i18ndude do its job collecting msgids
_ = lambda x:x.encode('utf-8')

SSLDisplayList = DisplayList((
    ('HTTP_SSL_PROTOCOL', 'The SSL protocol version', _(u'The SSL protocol version')),                 
    ('HTTP_SSL_SESSION_ID', 'The hex-encoded SSL session id', _(u'The hex-encoded SSL session id')),
    ('HTTP_SSL_CIPHER', 'The cipher specification name', _(u'The cipher specification name')),
    ('HTTP_SSL_CIPHER_EXPORT', 'true if cipher is an export cipher', _(u'true if cipher is an export cipher')),
    ('HTTP_SSL_CIPHER_USEKEYSIZE', 'Number of cipher bits (actually used)', _(u'Number of cipher bits (actually used)')),
    ('HTTP_SSL_CIPHER_ALGKEYSIZE', 'Number of cipher bits (possible)', _(u'Number of cipher bits (possible)')),
    ('HTTP_SSL_COMPRESS_METHOD', 'SSL compression method negotiated', _(u'SSL compression method negotiated')),
    ('HTTP_SSL_VERSION_INTERFACE', 'The mod_ssl program version', _(u'The mod_ssl program version')),
    ('HTTP_SSL_VERSION_LIBRARY', 'The OpenSSL program version', _(u'The OpenSSL program version')),
    ('HTTP_SSL_CLIENT_M_VERSION', 'The version of the client certificate', _(u'The version of the client certificate')),
    ('HTTP_SSL_CLIENT_M_SERIAL', 'The serial of the client certificate', _(u'The serial of the client certificate')),
    ('HTTP_SSL_CLIENT_S_DN', "One line representation of the client's certificate", _(u"One line representation of the client's certificate")),
    ('HTTP_SSL_CLIENT_S_DN_C', "Client's Country name", _(u"Client's Country name")),
    ('HTTP_SSL_CLIENT_S_DN_ST', "Client's State or province name", _(u"Client's State or province name")),
    ('HTTP_SSL_CLIENT_S_DN_L', "Client's Locality name", _(u"Client's Locality name")),
    ('HTTP_SSL_CLIENT_S_DN_O', "Client's Organization name", _(u"Client's Organization name")),
    ('HTTP_SSL_CLIENT_S_DN_OU', "Client's Organizational unit name", _(u"Client's Organizational unit name")),
    ('HTTP_SSL_CLIENT_S_DN_CN', "Client's Common name", _(u"Client's Common name")),
    ('HTTP_SSL_CLIENT_S_DN_T', "Client's Title", _(u"Client's Title")),
    ('HTTP_SSL_CLIENT_S_DN_I', "Client's Initials", _(u"Client's Initials")),
    ('HTTP_SSL_CLIENT_S_DN_G', "Client's Given name", _(u"Client's Given name")),
    ('HTTP_SSL_CLIENT_S_DN_S', "Client's Last name", _(u"Client's Last name")),
    ('HTTP_SSL_CLIENT_S_DN_D', "Client's Description", _(u"Client's Description")),
    ('HTTP_SSL_CLIENT_S_DN_UID', "Client's Unique identifier", _(u"Client's Unique identifier")),
    ('HTTP_SSL_CLIENT_S_DN_Email', "Client's Email address", _(u"Client's Email address")),
    ('HTTP_SSL_CLIENT_I_DN', "One line representation of the certificate issuer's certificate", _(u"One line representation of the certificate issuer's certificate")),
    ('HTTP_SSL_CLIENT_I_DN_C', "Certificate Issuer's Country name", _(u"Certificate Issuer's Country name")),
    ('HTTP_SSL_CLIENT_I_DN_ST', "Certificate Issuer's State or province name", _(u"Certificate Issuer's State or province name")),
    ('HTTP_SSL_CLIENT_I_DN_L', "Certificate Issuer's Locality name", _(u"Certificate Issuer's Locality name")),
    ('HTTP_SSL_CLIENT_I_DN_O', "Certificate Issuer's Organization name", _(u"Certificate Issuer's Organization name")),
    ('HTTP_SSL_CLIENT_I_DN_OU', "Certificate Issuer's Organizational unit name", _(u"Certificate Issuer's Organizational unit name")),
    ('HTTP_SSL_CLIENT_I_DN_CN', "Certificate Issuer's Common name", _(u"Certificate Issuer's Common name")),
    ('HTTP_SSL_CLIENT_I_DN_T', "Certificate Issuer's Title", _(u"Certificate Issuer's Title")),
    ('HTTP_SSL_CLIENT_I_DN_I', "Certificate Issuer's Initials", _(u"Certificate Issuer's Initials")),
    ('HTTP_SSL_CLIENT_I_DN_G', "Certificate Issuer's Given name", _(u"Certificate Issuer's Given name")),
    ('HTTP_SSL_CLIENT_I_DN_S', "Certificate Issuer's Last name", _(u"Certificate Issuer's Last name")),
    ('HTTP_SSL_CLIENT_I_DN_D', "Certificate Issuer's Description", _(u"Certificate Issuer's Description")),
    ('HTTP_SSL_CLIENT_I_DN_UID', "Certificate Issuer's Unique identifier", _(u"Certificate Issuer's Unique identifier")),
    ('HTTP_SSL_CLIENT_I_DN_Email', "Certificate Issuer's Email address", _(u"Certificate Issuer's Email address")),
    ('HTTP_SSL_CLIENT_V_START', "Validity of client's certificate (start time)", _(u"Validity of client's certificate (start time)")),
    ('HTTP_SSL_CLIENT_V_END', "Validity of client's certificate (end time)", _(u"Validity of client's certificate (end time)")),
    ('HTTP_SSL_CLIENT_V_REMAIN', "Number of days until client's certificate expires", _(u"Number of days until client's certificate expires")),
    ('HTTP_SSL_CLIENT_A_SIG', "Algorithm used for the signature of client's certificate", _(u"Algorithm used for the signature of client's certificate")),
    ('HTTP_SSL_CLIENT_CERT', 'PEM-encoded client certificate', _(u'PEM-encoded client certificate')),
    ('HTTP_SSL_SERVER_M_VERSION', 'The version of the server certificate', _(u'The version of the server certificate')),
    ('HTTP_SSL_SERVER_M_SERIAL', 'The serial of the server certificate', _(u'The serial of the server certificate')),
    ('HTTP_SSL_SERVER_S_DN', "One line representation of the server's certificate", _(u"One line representation of the server's certificate")),
    ('HTTP_SSL_SERVER_S_DN_C', "Server's Country name", _(u"Server's Country name")),
    ('HTTP_SSL_SERVER_S_DN_ST', "Server's State or province name", _(u"Server's State or province name")),
    ('HTTP_SSL_SERVER_S_DN_L', "Server's Locality name", _(u"Server's Locality name")),
    ('HTTP_SSL_SERVER_S_DN_O', "Server's Organization name", _(u"Server's Organization name")),
    ('HTTP_SSL_SERVER_S_DN_OU', "Server's Organizational unit name", _(u"Server's Organizational unit name")),
    ('HTTP_SSL_SERVER_S_DN_CN', "Server's Common name", _(u"Server's Common name")),
    ('HTTP_SSL_SERVER_S_DN_T', "Server's Title", _(u"Server's Title")),
    ('HTTP_SSL_SERVER_S_DN_I', "Server's Initials", _(u"Server's Initials")),
    ('HTTP_SSL_SERVER_S_DN_G', "Server's Given name", _(u"Server's Given name")),
    ('HTTP_SSL_SERVER_S_DN_S', "Server's Last name", _(u"Server's Last name")),
    ('HTTP_SSL_SERVER_S_DN_D', "Server's Description", _(u"Server's Description")),
    ('HTTP_SSL_SERVER_S_DN_UID', "Server's Unique identifier", _(u"Server's Unique identifier")),
    ('HTTP_SSL_SERVER_S_DN_Email', "Server's Email address", _(u"Server's Email address")),
    ('HTTP_SSL_SERVER_I_DN', "One line representation of the certificate issuer's certificate", _(u"One line representation of the certificate issuer's certificate")),
    ('HTTP_SSL_SERVER_I_DN_C', "Server's Certificate Issuer's Country name", _(u"Server's Certificate Issuer's Country name")),
    ('HTTP_SSL_SERVER_I_DN_ST', "Server's Certificate Issuer's State or province name", _(u"Server's Certificate Issuer's State or province name")),
    ('HTTP_SSL_SERVER_I_DN_L', "Server's Certificate Issuer's Locality name", _(u"Server's Certificate Issuer's Locality name")),
    ('HTTP_SSL_SERVER_I_DN_O', "Server's Certificate Issuer's Organization name", _(u"Server's Certificate Issuer's Organization name")),
    ('HTTP_SSL_SERVER_I_DN_OU', "Server's Certificate Issuer's Organizational unit name", _(u"Server's Certificate Issuer's Organizational unit name")),
    ('HTTP_SSL_SERVER_I_DN_CN', "Server's Certificate Issuer's Common name", _(u"Server's Certificate Issuer's Common name")),
    ('HTTP_SSL_SERVER_I_DN_T', "Server's Certificate Issuer's Title", _(u"Server's Certificate Issuer's Title")),
    ('HTTP_SSL_SERVER_I_DN_I', "Server's Certificate Issuer's Initials", _(u"Server's Certificate Issuer's Initials")),
    ('HTTP_SSL_SERVER_I_DN_G', "Server's Certificate Issuer's Given name", _(u"Server's Certificate Issuer's Given name")),
    ('HTTP_SSL_SERVER_I_DN_S', "Server's Certificate Issuer's Last name", _(u"Server's Certificate Issuer's Last name")),
    ('HTTP_SSL_SERVER_I_DN_D', "Server's Certificate Issuer's Description", _(u"Server's Certificate Issuer's Description")),
    ('HTTP_SSL_SERVER_I_DN_UID', "Server's Certificate Issuer's Unique identifier", _(u"Server's Certificate Issuer's Unique identifier")),
    ('HTTP_SSL_SERVER_I_DN_Email', "Server's Certificate Issuer's Email address", _(u"Server's Certificate Issuer's Email address")),
    ('HTTP_SSL_SERVER_V_START', "Validity of server's certificate (start time)", _(u"Validity of server's certificate (start time)")),
    ('HTTP_SSL_SERVER_V_END', "Validity of server's certificate (end time)", _(u"Validity of server's certificate (end time)")),
    ('HTTP_SSL_SERVER_A_SIG', "Algorithm used for the signature of server's certificate", _(u"Algorithm used for the signature of server's certificate")),
    ('HTTP_SSL_SERVER_A_KEY', "Algorithm used for the public key of server's certificate", _(u"Algorithm used for the public key of server's certificate")),
    ('HTTP_SSL_SERVER_CERT', 'PEM-encoded server certificate', _(u'PEM-encoded server certificate')),
    ))


sslfieldschema = fieldsBase.BaseFieldSchemaStringDefault.copy() + Schema((
        StringField('sslfield',
                    searchable=False,
                    required=True,
                    vocabulary=SSLDisplayList,
                    widget=SelectionWidget(
                       label=u'SSL variable to extract the value from',
                       label_msgid=_(u'SSL variable to extract the value from'),
                       description=u'Using this field, you can extract the values to populate it from the SSL certificate fields',
                       description_msgid=_(u'Using this field, you can extract the values to populate it from the SSL certificate fields'),
                       i18n_domain='collective.pfg.sslfield',
                       ),
                    ),
        ),)

# Disable fields we don't want to be editable
sslfieldschema['fgDefault'].widget.visible = {'view': 0, 'edit': 0}
sslfieldschema['fgTDefault'].widget.visible = {'view': 0, 'edit': 0}
sslfieldschema['fgTValidator'].widget.visible = {'view': 0, 'edit': 0}


class PFGSSLStringField(fields.FGStringField):
    """
       A PloneFormGen Form Field
    """

    security  = ClassSecurityInfo()

    schema = sslfieldschema

    def __init__(self, oid, **kwargs):
        """ initialize class """
        fields.FGStringField.__init__(self, oid, **kwargs)
        self.fgField.widget.macro = 'ssl_string_widget'

    def fgPrimeDefaults(self, request={}, contextObject=None):
        """ get the default value for this field exploring
            the request to get the SSL parameter's value
        """
        sslparam = self.getSslfield()
        if request.get('HTTP_SSL_CLIENT_VERIFY', '') == 'SUCCESS':
            value = request.get(sslparam, None)
        else:
            value = ''

        if value:
            request.form.setdefault(self.fgField.__name__, value)

registerATCT(PFGSSLStringField, PROJECTNAME)        
    
    
