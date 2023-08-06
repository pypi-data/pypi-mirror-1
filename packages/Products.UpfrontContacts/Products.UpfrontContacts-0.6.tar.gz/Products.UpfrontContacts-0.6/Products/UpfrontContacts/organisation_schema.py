from Products.Archetypes.public import *
from Products.ATExtensions.at_extensions import RecordWidget
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import \
    ReferenceBrowserWidget
from Products.UpfrontContacts.references import BidirectionalReference
from Products.UpfrontContacts.CustomFields import AddressField
from Products.UpfrontContacts.config import ACCOUNT_TYPES

schema = BaseFolderSchema.copy() + Schema((
    StringField('Name',
        required=1,
        searchable='1'),
    StringField('RegistrationNumber',
        widget=StringWidget(
            label='Registration number',
            label_msgid='label_registrationnumber',
        ),
    ),
    StringField('TaxNumber',
        widget=StringWidget(
            label='Tax number',
            label_msgid='label_taxnumber',
        ),
    ),
    DateTimeField('FormationDate',
        widget=CalendarWidget(
            label='Formation date',
            label_msgid='label_formationdate',
            show_hm=False,
            starting_year=1900,
        ),
    ),
    StringField('Size',
        widget=StringWidget(
            label='Number of employees',
            label_msgid='label_number_of_employees'
        ),
    ), 
    StringField('Phone',
        index='FieldIndex:brains',
        widget=StringWidget(
            label='Phone',
            label_msgid='label_phone',
        ),
    ),
    StringField('Fax',
        index='FieldIndex:brains',
        widget=StringWidget(
            label='Fax',
            label_msgid='label_fax',
        ),
    ),
    ImageField('Logo'),
    StringField('Email',
        schemata='Address',
        widget=StringWidget(
            label='Organisation email address',
            label_msgid='label_emailaddress'
        ),
        validators=('isEmail',)
    ),
    AddressField('PhysicalAddress',
        schemata='Address',
        widget=RecordWidget(
           macro='custom_address_widget',
           label='Physical address',
           label_msgid='label_physical_address',
        ),
    ),
    # Used as Metadata
    ComputedField('PhysicalAddressAsString',
        expression='here.getPhysicalAddressAsString()',
        index='FieldIndex:brains',
        widget=ComputedWidget(
            visible={'edit': 'hidden', 'view': 'invisible'}
        ),
    ),
    AddressField('PostalAddress',
        schemata='Address',
        widget=RecordWidget(
           macro='custom_address_widget',
           label='Postal address',
           label_msgid='label_postal_address',
        ),
    ),
    AddressField('BillingAddress',
        schemata='Address',
        widget=RecordWidget(
           macro='custom_address_widget',
           label='Billing address',
           label_msgid='label_billing_address',
        ),
    ),
    StringField('AccountType',
        schemata='Bank account',
        vocabulary=ACCOUNT_TYPES,
        widget=StringWidget(
            label='Type of account', 
            label_msgid='label_accounttype',
        ),
    ),
    StringField('AccountName',
        schemata='Bank account',
        widget=StringWidget(
            label='Account name',
            label_msgid='label_accountname',
        ),
    ),
    StringField('AccountNumber',
        schemata='Bank account',
        widget=StringWidget(
            label='Account number',
            label_msgid='label_accountnumber',
        ),
    ),
    StringField('BranchCode',
        schemata='Bank account',
        widget=StringWidget(
            label='Branch code',
            label_msgid='label_branchcode',
        ),
    ),
    StringField('BankName',
        schemata='Bank account',
        widget=StringWidget(
            label='Bank name',
            label_msgid='label_bankname',
        ),
    ),
    StringField('BankSwiftCode',
        schemata='Bank account',
        widget=StringWidget(
            label='Swift banking code',
            label_msgid='label_swift_banking_code',
        ),
    ),
    ReferenceField('Contacts',
        schemata='Contacts',
        multiValued=1,
        allowed_types=('Person',),
        referenceClass=BidirectionalReference,
        relationship='OrganisationContacts',
        widget=ReferenceBrowserWidget(
            label='Contacts',
            label_msgid='label_contacts',
        ),
    ),
    ReferenceField('Customers',
        schemata='Customers',
        multiValued=1,
        allowed_types=('Organisation', 'Person',),
        referenceClass=BidirectionalReference,
        relationship='OrganisationCustomers',
        widget=ReferenceBrowserWidget(
            label='Customers',
            label_msgid='label_customers',
        ),
    ),
    ReferenceField('Suppliers',
        schemata='Suppliers',
        multiValued=1,
        allowed_types=('Organisation', 'Person',),
        referenceClass=BidirectionalReference,
        relationship='OrganisationSuppliers',
        widget=ReferenceBrowserWidget(
            label='Suppliers',
            label_msgid='label_suppliers',
        ),
    ),
),
)

IdField = schema['id']
IdField.widget.visible = {'edit': 'visible', 'view': 'invisible'}
# Don't make title required - it will be computed from the Organisation's
# Name
TitleField = schema['title']
TitleField.required = 0
TitleField.widget.visible = {'edit': 'hidden', 'view': 'invisible'}

