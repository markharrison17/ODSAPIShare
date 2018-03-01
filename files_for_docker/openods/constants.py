ALLOW_DELTA_CHANGES = True

# Names of search parameters
ORG_NAME = "Name"
POSTCODE = "PostCode"
LAST_CHANGED_SINCE = "LastChangeDate"
STATUS = "Status"
PRIMARY_ROLE_CODE = "PrimaryRoleId"
NON_PRIMARY_ROLE_CODE = "NonPrimaryRoleId"
RECORD_CLASS = 'OrgRecordClass'
LIMIT = 'Limit'
OFFSET = 'Offset'
FORMAT = "_format"

FHIR_ORG_NAME = "name"
FHIR_ORG_NAME_CONTAINS = "name:contains"
FHIR_ORG_NAME_EXACT = "name:exact"
FHIR_STATUS_ARG = "active"
FHIR_POSTCODE = "address-postalcode"
FHIR_POSTCODE_CONTAINS = FHIR_POSTCODE + ":contains"
FHIR_POSTCODE_EXACT = FHIR_POSTCODE + ":exact"
FHIR_ADDRESS_CITY = "address-city"
FHIR_ADDRESS_CITY_CONTAINS = FHIR_ADDRESS_CITY + ":contains"
FHIR_ADDRESS_CITY_EXACT = FHIR_ADDRESS_CITY + ":exact"
FHIR_LIMIT = "_count"
FHIR_PAGE = "_page"
FHIR_PRIMARY_ROLE = "ods-org-primaryRole"
FHIR_ROLE = "ods-org-role"
FHIR_LAST_UPDATED = "_lastUpdated"
FHIR_IDENTIFIER = "identifier"
FHIR_ID = "_id"

# Endpoint definitions
FHIR_ORGANISATIONS_ENDPOINT = "FHIR/Organization"
FHIR_CAPABILITIES_ENDPOINT = "FHIR/metadata"
FHIR_ROLES_ENDPOINT = "FHIR/STU3/CodeSystem/ODSAPI-OrganizationRole-1"
ORGANISATIONS_ENDPOINT = "organisations"
SYNC_ENDPOINT = "sync"

FHIR_ACTIVE_PERIOD_URI = "https://fhir.nhs.uk/STU3/StructureDefinition/Extension-ODSAPI-ActivePeriod-1"
FHIR_ROLE_ACTIVE_PERIOD_URI = "activePeriod"
FHIR_ORGANIZATION_ROLE_URI = "https://fhir.nhs.uk/STU3/StructureDefinition/Extension-ODSAPI-OrganizationRole-1"
FHIR_ROLE_URI = "role"
# FHIR_ROLE_SYSTEM_URI = "https://fhir.nhs.uk/" + FHIR_ROLES_ENDPOINT
FHIR_ROLE_CODE_URI = "FHIR ROLE CODE PLACEHOLDER"
FHIR_STATUS_URI = "status"
FHIR_PRIMARY_ROLE_URI = "primaryRole"
# FHIR_PLACEHOLDER_URI = "PLACEHOLDER"
FHIR_ODSCODE_SYSTEM_URI = "https://fhir.nhs.uk/Id/ods-organization-code"
FHIR_RECORD_CLASS_URI = "https://fhir.nhs.uk/STU3/CodeSystem/ODSAPI-OrganizationRecordClass-1"
FHIR_DATE_TYPE_URI = "https://fhir.nhs.uk/STU3/StructureDefinition/Extension-ODSAPI-DateType-1"
FHIR_ORGANISATION_URI = "https://fhir.nhs.uk/STU3/StructureDefinition/ODSAPI-Organization-1"


FHIR_SUMMARY = "_summary"
FHIR_STATUS_ARG = "active"
CONTENT_TYPE = "Content-Type"

# Versioning
FHIR_ROLES_VERSION = "1.0.0"

# Default Values
LIMIT_MIN = 1
LIMIT_MAX = 1000
OFFSET_MIN = 1
LIMIT_DEFAULT = 20
OFFSET_DEFAULT = 0
FHIR_PAGE_DEFAULT = 1
FHIR_PAGE_MIN = 1
FHIR_LIMIT_DEFAULT = 20
FHIR_LIMIT_MIN = 0
FHIR_LIMIT_MAX = 20

# Allowed formats
XML = "xml"
JSON = "json"


# Returned Header values and keys
APPLICATION_JSON = "application/json"
APPLICATION_XML = "application/xml"
RETURNED_RECORDS = "Returned-Records"
PREVIOUS_PAGE_LINK = "Previous-Page"
NEXT_PAGE_LINK = "Next-Page"

# Page links
LINK_RELATION_SELF = "self"
LINK_RELATION_FIRST = "first"
LINK_RELATION_LAST = "last"
LINK_RELATION_NEXT = "next"
LINK_RELATION_PREVIOUS = "previous"


# Allowed Status
ACTIVE = "ACTIVE"
INACTIVE = "INACTIVE"

# Allowed Summary value
FHIR_SUMMARY_COUNT = "count"


FHIR_ACTIVE_ARG = "true"
FHIR_INACTIVE_ARG = "false"


# Error messages returned
INVALID_DATE_FORMAT = "Date format must be YYYY-MM-DD."
INVALID_FUTURE_DATE = "Supplied " + LAST_CHANGED_SINCE + " date must be a past date, not future."
INVALID_PAST_DATE = "Supplied " + LAST_CHANGED_SINCE + " exceeds the limit of 185 days past."
INVALID_DATE = "Invalid date supplied."
ORG_NAME_TOO_SHORT = "Supplied " + ORG_NAME + " needs a minimum of 3 Characters."
ORG_NAME_TOO_LONG = "Supplied " + ORG_NAME + " too long, max 100 Characters."
ORG_NAME_INVALID_CHARACTER = "Supplied " + ORG_NAME + " contains invalid Character/s."
STATUS_UNKNOWN = "Unknown " + STATUS + " supplied, specify Active or Inactive."
POSTCODE_INVALID = "Supplied " + POSTCODE + " format is invalid."
POSTCODE_TOO_SHORT = "Supplied " + POSTCODE + " is too short, min 2 Characters."
UNKNOWN_REQUEST_ARG = "Unknown argument found."
UNKNOWN_FHIR_REQUEST_ARG = "Unknown argument found - {0}"
UNKNOWN_FHIR_REQUEST_ARG = "Unknown argument found - {0}"
INVALID_ROLE_CODE = "Supplied {0} is invalid."
INVALID_RECORD_CLASS = "Supplied " + RECORD_CLASS + " is invalid."
INVALID_LIMIT = str.format("Supplied {0} must be between {1} and {2}", LIMIT, LIMIT_MIN, LIMIT_MAX)
INVALID_OFFSET = str.format("Suppied {0} must be greater than {1}", OFFSET, OFFSET_MIN)
INSUFFICIANT_REQUIRED_ARGS = "Supplied query must include some query parameters"
REPEATED_ARGUMENT = "Repeated {0} argument."
FHIR_ORG_NAME_TOO_SHORT = "Supplied {0} needs a minimum of 3 Characters."
FHIR_ORG_NAME_TOO_LONG = "Supplied {0} too long, max 100 Characters."
FHIR_ORG_NAME_INVALID_CHARACTER = "Supplied {0} has invalid Character/s."
FHIR_INVALID_LIMIT = "Supplied limit is invalid, the parameter must take an integer between " + str(FHIR_LIMIT_MIN) + \
                     " and " + str(FHIR_LIMIT_MAX)
FHIR_INVALID_STATUS = "Supplied " + FHIR_STATUS_ARG + " parameter is invalid, must be 'true' or 'false'"
FHIR_INVALID_POSTCODE_ILLEGAL_CHAR = "Supplied " + FHIR_POSTCODE + " contains invalid characters, alphanumeric " \
                                                                   "characters only."
FHIR_INVALID_POSTCODE_TOO_LONG = "Supplied " + FHIR_POSTCODE + " is too long, max 8 characters."
FHIR_POSTCODE_TOO_SHORT = "Supplied " + FHIR_POSTCODE + " is too short, min 2 characters."
INVALID_FHIR_SUMMARY_PARAMETER = "Invalid " + FHIR_SUMMARY + " parameter."
FHIR_INVALID_STATUS = "Invalid FHIR " + FHIR_STATUS_ARG + " parameter"
FHIR_INVALID_CITY_SHORT = "Supplied " + FHIR_ADDRESS_CITY + " is too short, min 3 characters"
FHIR_INVALID_CITY_LONG = "Supplied " + FHIR_ADDRESS_CITY + " is too long, max 75 characters"
FHIR_INVALID_CITY_CHARACTERS = "Supplied " + FHIR_ADDRESS_CITY + " contains invalid characters, valid characters " \
                                                                 "include:  , . - ' and alphabetical characters"
TOO_MANY_FHIR_PRIMARY_ROLE_PARAMS = "Only one " + FHIR_PRIMARY_ROLE + " parameter should be supplied"
FHIR_INVALID_PRIMARY_ROLE = "Invalid FHIR " + FHIR_PRIMARY_ROLE + " parameter. Must be " \
                          + FHIR_ACTIVE_ARG + " or " + FHIR_INACTIVE_ARG + "."
FHIR_INVALID_ROLE = "Invalid FHIR " + FHIR_ROLE + " parameter"
INVALID_FHIR_ROLE_SYSTEM_URI = "Invalid " + FHIR_ROLE + " parameter. Should be {0}api/" + FHIR_ROLES_ENDPOINT + "."
FHIR_INVALID_DATE = "Supplied date is invalid"
FHIR_INVALID_LASTUPDATED_DATE_PREFIX = "Supplied date prefix is invalid, must be gt"
FHIR_PRIMARY_ROLE_WITHOUT_ROLE = FHIR_ROLE + " is a mandatory argument in all queries containing a " + FHIR_PRIMARY_ROLE + \
                                 " term."
INVALID_FHIR_IDENTIFIER = "Supplied identifier must be just alphanumeric characters."
INVALID_FHIR_ID = "Supplied _id must be just alphanumeric characters."
INVALID_FHIR_ODSCODE_SYSTEM_URI = "Invalid " + FHIR_ROLE + " parameter. Should be " + FHIR_ODSCODE_SYSTEM_URI + "."
FHIR_INVALID_PAGE = "page must be a number larger than 0"



# Contact Types
CONTACT_TEL = "tel"
CONTACT_FAX = "fax"
CONTACT_MAIL = "mailto"
CONTACT_HTTP = "http"

# FHIR Contact Types
FHIR_CONTACT_PHONE = "phone"
FHIR_CONTACT_FAX = "fax"
FHIR_CONTACT_EMAIL = "email"
FHIR_CONTACT_URL = "url"

STATUS_ACTIVE = "Active"
STATUS_INACTIVE = "Inactive"

FORMAT_FHIR_APPLICATION_JSON = "application/fhir+json"
FORMAT_FHIR_APPLICATION_JSON_2 = "application/json+fhir"
FORMAT_FHIR_APPLICATION_XML = "application/fhir+xml"
FORMAT_FHIR_APPLICATION_XML_2 = "application/xml+fhir"
TEXT_JSON = "text/json"
TEXT_XML = 'text/xml'


DATE_TYPE_OPERATIONAL = "Operational"
DATE_TYPE_LEGAL = "Legal"

FHIR_BUNDLE_SEARCHSET = "searchset"

XML_TAG = "<?xml version='1.0' encoding='UTF-8'?>"
FHIR_NAMESPACE = 'xmlns="http://hl7.org/fhir"'

# Table names and table alias'


# FHIR ROLE CODE ENDPOINT CONSTANTS
FHIR_ROLES_ENDPOINT_NAME = "ODS API Organization Role"
FHIR_ROLES_ENDPOINT_STATUS = "active"
FHIR_ROLES_ENDPOINT_PUBLISHER = "NHS Digital"
FHIR_ROLES_ENDPOINT_DESCRIPTION = "A CodeSystem that identifies the role(s) of the organization."
FHIR_ROLES_ENDPOINT_COPYRIGHT = "Copyright © 2017 Health and Social Care Information Centre. NHS Digital is the trad" \
                               "ing name of the Health and Social Care Information Centre."
FHIR_ROLES_ENDPOINT_CONTENT = "complete"
FHIR_ROLES_ENDPOINT_CONTACT_NAME = "National Helpdesk Exeter"
FHIR_ROLES_ENDPOINT_TELECOM_EMAIL = "exeter.helpdesk@nhs.net"
FHIR_ROLES_ENDPOINT_TELECOM_USE = "work"
FHIR_ROLES_ENDPOINT_TELECOM_PHONE_NO = "0300 303 4034"

INVALID_PARAMETER_ERROR = "INVALID_PARAMETER"
INVALID_VALUE_ERROR = "INVALID_VALUE"
INVALID_CODE_SYSTEM_ERROR = "INVALID_CODE_SYSTEM"
INVALID_CODE_VALUE_ERROR = "INVALID_CODE_VALUE"
INVALID_IDENTIFIER_SYSTEM_ERROR = "INVALID_IDENTIFIER_SYSTEM"
INVALID_IDENTIFIER_VALUE_ERROR = "INVALID_IDENTIFIER_VALUE"
NO_RECORD_FOUND_ERROR = "NO_RECORD_FOUND"
ACCESS_DENIED = "ACCESS DENIED"     #Intentionally without an _. DO NOT CHANGE


# LOG RELATED
SUCCESS = "SUCCESS"
FAILURE = "FAILURE"
SERVICE = "SERVICE"
TRANSLATION = "TRANSLATION"
SERIALISATION = "SERIALISATION"
MODEL = "MODEL"


#ORD  TRANLSTAION, SERIALISATION RELATED
ORGANISATION = "Organisation"
ADDRESS = "Address"
DATES = 'Date'
RELS = "Rels"
ROLES = "Roles"
SUCCS = "Succs"
CONTACTS = "Contacts"
RELATIONSHIP = "Relationships"
SUCCESSORS = "Successors"



FILE_LOCATION_PATH = '/Users/markharrison/delta_data/'
CURRENT_SCHEMA_FILE = 'current_schema.xsd'
GIT_HUB = "https://raw.githubusercontent.com/ODS-API/delta_files/master/"

THREADS_TO_RUN = 'threads_to_run.txt'

CONNECTION_POOL_SIZE = 20
SCHEMA_VERSION = '015'

LIVE_DATABASE = "import_test"
BACKUP_DATABASE = "import_test_backup"
NEW_BACKUP_DATABASE = "import_test_backup_new"
ARCHIVED_DATABASE = "import_test_old"

DAY_IN_SECONDS = 86400

SENDING_EMAIL = "kamdevtest@gmail.com"
RECIPIENT_EMAIL = "mark.harrison17@nhs.net"

MAX_DAYS_FUTURE_UPLOAD = 5

