from Products.Archetypes.public import *
from Products.remember.content.member_schema import id_schema, \
    contact_schema, plone_schema, security_schema, login_info_schema
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import \
    ReferenceBrowserWidget
from Products.ATExtensions.at_extensions import RecordWidget
from Products.UpfrontContacts.CustomFields import AddressField
from Products.UpfrontContacts.references import BidirectionalReference
from Products.UpfrontContacts.config import ACCOUNT_TYPES, GENDERS

person_schema = Schema((
    StringField('FirstName',
        required=1,
        widget=StringWidget(
            label='First Name', 
            label_msgid='label_firstname',
        ),
        regfield=1,
        user_property=True,
    ),
    StringField('LastName',
        required=1,
        widget=StringWidget(
            label='Last Name', 
            label_msgid='label_lastname',
        ),
        regfield=1,
        user_property=True,
    ),
    contact_schema['email'],
    id_schema['id'],
    id_schema['title'],
    security_schema['password'],
    security_schema['confirm_password'],
    security_schema['mail_me'],
    ComputedField('fullname',
        expression='context.getFullname()',
        searchable=1,
        widget=ComputedWidget(
            label='Full name',
            label_msgid='label_fullname', 
            visible={'edit': 'invisible', 'view': 'invisible'},
        ),
        user_property=True,
    ),
    ReferenceField('Organisation',
        allowed_types=('Organisation',),
        relationship='OrganisationContacts',
        referenceClass=BidirectionalReference,
        widget=ReferenceBrowserWidget,
        user_property=False,
    ),
    # For easy querying of Company Contact relationship
    ComputedField('OrganisationUID',
        expression='here.getOrganisation() and here.getOrganisation().UID() or None',
        index='FieldIndex:brains',
        widget=ComputedWidget(
            visible={'edit': 'hidden', 'view': 'invisible'},
        ),
        user_property=False,
    ),
    StringField('Department',
        searchable=1,
        widget=StringWidget(
            label='Department', 
            label_msgid='label_department',
        ),
        user_property=True,
    ),
    StringField('BusinessPhone',
        index='FieldIndex:brains',
        widget=StringWidget(
            label='Business Phone', 
            label_msgid='label_phone_business',
        ),
        user_property=True,
    ),
    StringField('BusinessFax',
        index='FieldIndex:brains',
        widget=StringWidget(
            label='Business Fax', 
            label_msgid='label_fax_business',
        ),
        user_property=True,
    ),
    StringField('HomePhone',
        index='FieldIndex:brains',
        widget=StringWidget(
            label='Home Phone', 
            label_msgid='label_phone_home',
        ),
        user_property=True,
    ),
    StringField('MobilePhone',
        index='FieldIndex:brains',
        widget=StringWidget(
            label='Mobile Phone', 
            label_msgid='label_phone_mobile',
        ),
        user_property=True,
    ),
))

address_schema = Schema((
    AddressField('PhysicalAddress',
        schemata='Address',
        widget=RecordWidget(
           macro='custom_address_widget',
           label='Physical address',
           label_msgid='label_physical_address',
        ),
        user_property=False,
    ),
    AddressField('PostalAddress',
        schemata='Address',
        widget=RecordWidget(
           macro='custom_address_widget',
           label='Postal address',
           label_msgid='label_postal_address',
        ),
        user_property=False,
    ),
))

personal_schema = Schema((
    DateTimeField('BirthDate',
        schemata='Personal',
        widget=CalendarWidget(
            label='Birth date',
            label_msgid='label_birthDate',
            starting_year=1900,
        ),
        user_property=True,
    ),
    StringField('BirthPlace',
        schemata='Personal',
        widget=StringWidget(
            label='Birth place',
            label_msgid='label_birthplace',
        ),
        user_property=True,
    ),
    StringField('Age',
        schemata='Personal',
        widget=StringWidget(
            label='Age', 
            label_msgid='label_age',
            description="Exact age as free text eg. 25 years",
            description_msgid="help_age"
        ),
        user_property=True,
    ),
    StringField('Gender',
        schemata='Personal',
        vocabulary=GENDERS,
        widget=SelectionWidget(
            label='Gender',
            label_msgid='label_gender',
        ),
        user_property=True,
    ),
))

bank_account_schema = Schema((
    StringField('AccountType',
        schemata='Bank account',
        vocabulary=ACCOUNT_TYPES,
        widget=StringWidget(
            label='Type of account', 
            label_msgid='label_accounttype',
        ),
        user_property=True,
    ),
    StringField('AccountNumber',
        schemata='Bank account',
        widget=StringWidget(
            label='Account number',
            label_msgid='label_accountnumber',
        ),
        user_property=True,
    ),
    StringField('BranchNumber',
        schemata='Bank account',
        widget=StringWidget(
            label='Branch number',
            label_msgid='label_branchnumber',
        ),
        user_property=True,
    ),
    StringField('BankName',
        schemata='Bank account',
        widget=StringWidget(
            label='Bank name',
            label_msgid='label_bankname',
        ),
        user_property=True,
    ),
))

plone_schema = plone_schema.copy()
for field in plone_schema.fields():
    field.schemata = 'Plone-Settings'

security_schema = security_schema.copy()
del security_schema['password'],
del security_schema['confirm_password'],
del security_schema['mail_me'],
for field in security_schema.fields():
    field.schemata = 'Security'

#property sheets can't handle images
plone_schema['portrait'].user_property = False

metadata_schema = ExtensibleMetadata.schema.copy()
person_schema = (
    person_schema + address_schema + personal_schema + security_schema +
    plone_schema + login_info_schema + metadata_schema
    )

TitleField = person_schema['title']
TitleField.required = 0
TitleField.widget.visible = False

