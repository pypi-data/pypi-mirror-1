"""extracts TNEF encoded content from for example winmail.dat attachments.

Example usage:

T = TNEF(open("winmail.dat").read())
print "Key:", T.key
for o in T.objects:
   print "Object: ", TNEF.codes[o.name]
for a in T.attachments:
   print "Attachment: ", a.long_filename()
"""

def debug(str):
   "debug utility"
   print str

def bytes_to_int(bytes=None):
   "transform multi-byte values into integers"
   n = num = 0
   for b in bytes:
      num += ( ord(b) << n)
      n += 8
   return num

class TNEFMAPI_Attribute:
   "represents a mapi attribute"

   MAPI_ACKNOWLEDGEMENT_MODE = 0x0001
   MAPI_ALTERNATE_RECIPIENT_ALLOWED = 0x0002
   MAPI_AUTHORIZING_USERS = 0x0003
   MAPI_AUTO_FORWARD_COMMENT = 0x0004
   MAPI_AUTO_FORWARDED = 0x0005
   MAPI_CONTENT_CONFIDENTIALITY_ALGORITHM_ID = 0x0006
   MAPI_CONTENT_CORRELATOR = 0x0007
   MAPI_CONTENT_IDENTIFIER = 0x0008
   MAPI_CONTENT_LENGTH = 0x0009
   MAPI_CONTENT_RETURN_REQUESTED = 0x000A
   MAPI_CONVERSATION_KEY = 0x000B
   MAPI_CONVERSION_EITS = 0x000C
   MAPI_CONVERSION_WITH_LOSS_PROHIBITED = 0x000D
   MAPI_CONVERTED_EITS = 0x000E
   MAPI_DEFERRED_DELIVERY_TIME = 0x000F
   MAPI_DELIVER_TIME = 0x0010
   MAPI_DISCARD_REASON = 0x0011
   MAPI_DISCLOSURE_OF_RECIPIENTS = 0x0012
   MAPI_DL_EXPANSION_HISTORY = 0x0013
   MAPI_DL_EXPANSION_PROHIBITED = 0x0014
   MAPI_EXPIRY_TIME = 0x0015
   MAPI_IMPLICIT_CONVERSION_PROHIBITED = 0x0016
   MAPI_IMPORTANCE = 0x0017
   MAPI_IPM_ID = 0x0018
   MAPI_LATEST_DELIVERY_TIME = 0x0019
   MAPI_MESSAGE_CLASS = 0x001A
   MAPI_MESSAGE_DELIVERY_ID = 0x001B
   MAPI_MESSAGE_SECURITY_LABEL = 0x001E
   MAPI_OBSOLETED_IPMS = 0x001F
   MAPI_ORIGINALLY_INTENDED_RECIPIENT_NAME = 0x0020
   MAPI_ORIGINAL_EITS = 0x0021
   MAPI_ORIGINATOR_CERTIFICATE = 0x0022
   MAPI_ORIGINATOR_DELIVERY_REPORT_REQUESTED = 0x0023
   MAPI_ORIGINATOR_RETURN_ADDRESS = 0x0024
   MAPI_PARENT_KEY = 0x0025
   MAPI_PRIORITY = 0x0026
   MAPI_ORIGIN_CHECK = 0x0027
   MAPI_PROOF_OF_SUBMISSION_REQUESTED = 0x0028
   MAPI_READ_RECEIPT_REQUESTED = 0x0029
   MAPI_RECEIPT_TIME = 0x002A
   MAPI_RECIPIENT_REASSIGNMENT_PROHIBITED = 0x002B
   MAPI_REDIRECTION_HISTORY = 0x002C
   MAPI_RELATED_IPMS = 0x002D
   MAPI_ORIGINAL_SENSITIVITY = 0x002E
   MAPI_LANGUAGES = 0x002F
   MAPI_REPLY_TIME = 0x0030
   MAPI_REPORT_TAG = 0x0031
   MAPI_REPORT_TIME = 0x0032
   MAPI_RETURNED_IPM = 0x0033
   MAPI_SECURITY = 0x0034
   MAPI_INCOMPLETE_COPY = 0x0035
   MAPI_SENSITIVITY = 0x0036
   MAPI_SUBJECT = 0x0037
   MAPI_SUBJECT_IPM = 0x0038
   MAPI_CLIENT_SUBMIT_TIME = 0x0039
   MAPI_REPORT_NAME = 0x003A
   MAPI_SENT_REPRESENTING_SEARCH_KEY = 0x003B
   MAPI_X400_CONTENT_TYPE = 0x003C
   MAPI_SUBJECT_PREFIX = 0x003D
   MAPI_NON_RECEIPT_REASON = 0x003E
   MAPI_RECEIVED_BY_ENTRYID = 0x003F
   MAPI_RECEIVED_BY_NAME = 0x0040
   MAPI_SENT_REPRESENTING_ENTRYID = 0x0041
   MAPI_SENT_REPRESENTING_NAME = 0x0042
   MAPI_RCVD_REPRESENTING_ENTRYID = 0x0043
   MAPI_RCVD_REPRESENTING_NAME = 0x0044
   MAPI_REPORT_ENTRYID = 0x0045
   MAPI_READ_RECEIPT_ENTRYID = 0x0046
   MAPI_MESSAGE_SUBMISSION_ID = 0x0047
   MAPI_PROVIDER_SUBMIT_TIME = 0x0048
   MAPI_ORIGINAL_SUBJECT = 0x0049
   MAPI_DISC_VAL = 0x004A
   MAPI_ORIG_MESSAGE_CLASS = 0x004B
   MAPI_ORIGINAL_AUTHOR_ENTRYID = 0x004C
   MAPI_ORIGINAL_AUTHOR_NAME = 0x004D
   MAPI_ORIGINAL_SUBMIT_TIME = 0x004E
   MAPI_REPLY_RECIPIENT_ENTRIES = 0x004F
   MAPI_REPLY_RECIPIENT_NAMES = 0x0050
   MAPI_RECEIVED_BY_SEARCH_KEY = 0x0051
   MAPI_RCVD_REPRESENTING_SEARCH_KEY = 0x0052
   MAPI_READ_RECEIPT_SEARCH_KEY = 0x0053
   MAPI_REPORT_SEARCH_KEY = 0x0054
   MAPI_ORIGINAL_DELIVERY_TIME = 0x0055
   MAPI_ORIGINAL_AUTHOR_SEARCH_KEY = 0x0056
   MAPI_MESSAGE_TO_ME = 0x0057
   MAPI_MESSAGE_CC_ME = 0x0058
   MAPI_MESSAGE_RECIP_ME = 0x0059
   MAPI_ORIGINAL_SENDER_NAME = 0x005A
   MAPI_ORIGINAL_SENDER_ENTRYID = 0x005B
   MAPI_ORIGINAL_SENDER_SEARCH_KEY = 0x005C
   MAPI_ORIGINAL_SENT_REPRESENTING_NAME = 0x005D
   MAPI_ORIGINAL_SENT_REPRESENTING_ENTRYID = 0x005E
   MAPI_ORIGINAL_SENT_REPRESENTING_SEARCH_KEY = 0x005F
   MAPI_START_DATE = 0x0060
   MAPI_END_DATE = 0x0061
   MAPI_OWNER_APPT_ID = 0x0062
   MAPI_RESPONSE_REQUESTED = 0x0063
   MAPI_SENT_REPRESENTING_ADDRTYPE = 0x0064
   MAPI_SENT_REPRESENTING_EMAIL_ADDRESS = 0x0065
   MAPI_ORIGINAL_SENDER_ADDRTYPE = 0x0066
   MAPI_ORIGINAL_SENDER_EMAIL_ADDRESS = 0x0067
   MAPI_ORIGINAL_SENT_REPRESENTING_ADDRTYPE = 0x0068
   MAPI_ORIGINAL_SENT_REPRESENTING_EMAIL_ADDRESS = 0x0069
   MAPI_CONVERSATION_TOPIC = 0x0070
   MAPI_CONVERSATION_INDEX = 0x0071
   MAPI_ORIGINAL_DISPLAY_BCC = 0x0072
   MAPI_ORIGINAL_DISPLAY_CC = 0x0073
   MAPI_ORIGINAL_DISPLAY_TO = 0x0074
   MAPI_RECEIVED_BY_ADDRTYPE = 0x0075
   MAPI_RECEIVED_BY_EMAIL_ADDRESS = 0x0076
   MAPI_RCVD_REPRESENTING_ADDRTYPE = 0x0077
   MAPI_RCVD_REPRESENTING_EMAIL_ADDRESS = 0x0078
   MAPI_ORIGINAL_AUTHOR_ADDRTYPE = 0x0079
   MAPI_ORIGINAL_AUTHOR_EMAIL_ADDRESS = 0x007A
   MAPI_ORIGINALLY_INTENDED_RECIP_ADDRTYPE = 0x007B
   MAPI_ORIGINALLY_INTENDED_RECIP_EMAIL_ADDRESS = 0x007C
   MAPI_TRANSPORT_MESSAGE_HEADERS = 0x007D
   MAPI_DELEGATION = 0x007E
   MAPI_TNEF_CORRELATION_KEY = 0x007F
   MAPI_BODY = 0x1000
   MAPI_REPORT_TEXT = 0x1001
   MAPI_ORIGINATOR_AND_DL_EXPANSION_HISTORY = 0x1002
   MAPI_REPORTING_DL_NAME = 0x1003
   MAPI_REPORTING_MTA_CERTIFICATE = 0x1004

   MAPI_RTF_SYNC_BODY_CRC = 0x1006
   MAPI_RTF_SYNC_BODY_COUNT = 0x1007
   MAPI_RTF_SYNC_BODY_TAG = 0x1008
   MAPI_RTF_COMPRESSED = 0x1009
   MAPI_RTF_SYNC_PREFIX_COUNT = 0x1010
   MAPI_RTF_SYNC_TRAILING_COUNT = 0x1011
   MAPI_ORIGINALLY_INTENDED_RECIP_ENTRYID = 0x1012
   MAPI_CONTENT_INTEGRITY_CHECK = 0x0C00
   MAPI_EXPLICIT_CONVERSION = 0x0C01
   MAPI_IPM_RETURN_REQUESTED = 0x0C02
   MAPI_MESSAGE_TOKEN = 0x0C03
   MAPI_NDR_REASON_CODE = 0x0C04
   MAPI_NDR_DIAG_CODE = 0x0C05
   MAPI_NON_RECEIPT_NOTIFICATION_REQUESTED = 0x0C06
   MAPI_DELIVERY_POINT = 0x0C07
   MAPI_ORIGINATOR_NON_DELIVERY_REPORT_REQUESTED = 0x0C08
   MAPI_ORIGINATOR_REQUESTED_ALTERNATE_RECIPIENT = 0x0C09
   MAPI_PHYSICAL_DELIVERY_BUREAU_FAX_DELIVERY = 0x0C0A
   MAPI_PHYSICAL_DELIVERY_MODE = 0x0C0B
   MAPI_PHYSICAL_DELIVERY_REPORT_REQUEST = 0x0C0C
   MAPI_PHYSICAL_FORWARDING_ADDRESS = 0x0C0D
   MAPI_PHYSICAL_FORWARDING_ADDRESS_REQUESTED = 0x0C0E
   MAPI_PHYSICAL_FORWARDING_PROHIBITED = 0x0C0F
   MAPI_PHYSICAL_RENDITION_ATTRIBUTES = 0x0C10
   MAPI_PROOF_OF_DELIVERY = 0x0C11
   MAPI_PROOF_OF_DELIVERY_REQUESTED = 0x0C12
   MAPI_RECIPIENT_CERTIFICATE = 0x0C13
   MAPI_RECIPIENT_NUMBER_FOR_ADVICE = 0x0C14
   MAPI_RECIPIENT_TYPE = 0x0C15
   MAPI_REGISTERED_MAIL_TYPE = 0x0C16
   MAPI_REPLY_REQUESTED = 0x0C17
   MAPI_REQUESTED_DELIVERY_METHOD = 0x0C18
   MAPI_SENDER_ENTRYID = 0x0C19
   MAPI_SENDER_NAME = 0x0C1A
   MAPI_SUPPLEMENTARY_INFO = 0x0C1B
   MAPI_TYPE_OF_MTS_USER = 0x0C1C
   MAPI_SENDER_SEARCH_KEY = 0x0C1D
   MAPI_SENDER_ADDRTYPE = 0x0C1E
   MAPI_SENDER_EMAIL_ADDRESS = 0x0C1F
   MAPI_CURRENT_VERSION = 0x0E00
   MAPI_DELETE_AFTER_SUBMIT = 0x0E01
   MAPI_DISPLAY_BCC = 0x0E02
   MAPI_DISPLAY_CC = 0x0E03
   MAPI_DISPLAY_TO = 0x0E04
   MAPI_PARENT_DISPLAY = 0x0E05
   MAPI_MESSAGE_DELIVERY_TIME = 0x0E06
   MAPI_MESSAGE_FLAGS = 0x0E07
   MAPI_MESSAGE_SIZE = 0x0E08
   MAPI_PARENT_ENTRYID = 0x0E09
   MAPI_SENTMAIL_ENTRYID = 0x0E0A
   MAPI_CORRELATE = 0x0E0C
   MAPI_CORRELATE_MTSID = 0x0E0D
   MAPI_DISCRETE_VALUES = 0x0E0E
   MAPI_RESPONSIBILITY = 0x0E0F
   MAPI_SPOOLER_STATUS = 0x0E10
   MAPI_TRANSPORT_STATUS = 0x0E11
   MAPI_MESSAGE_RECIPIENTS = 0x0E12
   MAPI_MESSAGE_ATTACHMENTS = 0x0E13
   MAPI_SUBMIT_FLAGS = 0x0E14
   MAPI_RECIPIENT_STATUS = 0x0E15
   MAPI_TRANSPORT_KEY = 0x0E16
   MAPI_MSG_STATUS = 0x0E17
   MAPI_MESSAGE_DOWNLOAD_TIME = 0x0E18
   MAPI_CREATION_VERSION = 0x0E19
   MAPI_MODIFY_VERSION = 0x0E1A
   MAPI_HASATTACH = 0x0E1B
   MAPI_BODY_CRC = 0x0E1C
   MAPI_NORMALIZED_SUBJECT = 0x0E1D
   MAPI_RTF_IN_SYNC = 0x0E1F
   MAPI_ATTACH_SIZE = 0x0E20
   MAPI_ATTACH_NUM = 0x0E21
   MAPI_PREPROCESS = 0x0E22
   MAPI_ORIGINATING_MTA_CERTIFICATE = 0x0E25
   MAPI_PROOF_OF_SUBMISSION = 0x0E26
   MAPI_ENTRYID = 0x0FFF
   MAPI_OBJECT_TYPE = 0x0FFE
   MAPI_ICON = 0x0FFD
   MAPI_MINI_ICON = 0x0FFC
   MAPI_STORE_ENTRYID = 0x0FFB
   MAPI_STORE_RECORD_KEY = 0x0FFA
   MAPI_RECORD_KEY = 0x0FF9
   MAPI_MAPPING_SIGNATURE = 0x0FF8
   MAPI_ACCESS_LEVEL = 0x0FF7
   MAPI_INSTANCE_KEY = 0x0FF6
   MAPI_ROW_TYPE = 0x0FF5
   MAPI_ACCESS = 0x0FF4
   MAPI_ROWID = 0x3000
   MAPI_DISPLAY_NAME = 0x3001
   MAPI_ADDRTYPE = 0x3002
   MAPI_EMAIL_ADDRESS = 0x3003
   MAPI_COMMENT = 0x3004
   MAPI_DEPTH = 0x3005
   MAPI_PROVIDER_DISPLAY = 0x3006
   MAPI_CREATION_TIME = 0x3007
   MAPI_LAST_MODIFICATION_TIME = 0x3008
   MAPI_RESOURCE_FLAGS = 0x3009
   MAPI_PROVIDER_DLL_NAME = 0x300A
   MAPI_SEARCH_KEY = 0x300B
   MAPI_PROVIDER_UID = 0x300C
   MAPI_PROVIDER_ORDINAL = 0x300D
   MAPI_FORM_VERSION = 0x3301
   MAPI_FORM_CLSID = 0x3302
   MAPI_FORM_CONTACT_NAME = 0x3303
   MAPI_FORM_CATEGORY = 0x3304
   MAPI_FORM_CATEGORY_SUB = 0x3305
   MAPI_FORM_HOST_MAP = 0x3306
   MAPI_FORM_HIDDEN = 0x3307
   MAPI_FORM_DESIGNER_NAME = 0x3308
   MAPI_FORM_DESIGNER_GUID = 0x3309
   MAPI_FORM_MESSAGE_BEHAVIOR = 0x330A
   MAPI_DEFAULT_STORE = 0x3400
   MAPI_STORE_SUPPORT_MASK = 0x340D
   MAPI_STORE_STATE = 0x340E
   MAPI_IPM_SUBTREE_SEARCH_KEY = 0x3410
   MAPI_IPM_OUTBOX_SEARCH_KEY = 0x3411
   MAPI_IPM_WASTEBASKET_SEARCH_KEY = 0x3412
   MAPI_IPM_SENTMAIL_SEARCH_KEY = 0x3413
   MAPI_MDB_PROVIDER = 0x3414
   MAPI_RECEIVE_FOLDER_SETTINGS = 0x3415
   MAPI_VALID_FOLDER_MASK = 0x35DF
   MAPI_IPM_SUBTREE_ENTRYID = 0x35E0
   MAPI_IPM_OUTBOX_ENTRYID = 0x35E2
   MAPI_IPM_WASTEBASKET_ENTRYID = 0x35E3
   MAPI_IPM_SENTMAIL_ENTRYID = 0x35E4
   MAPI_VIEWS_ENTRYID = 0x35E5
   MAPI_COMMON_VIEWS_ENTRYID = 0x35E6
   MAPI_FINDER_ENTRYID = 0x35E7
   MAPI_CONTAINER_FLAGS = 0x3600
   MAPI_FOLDER_TYPE = 0x3601
   MAPI_CONTENT_COUNT = 0x3602
   MAPI_CONTENT_UNREAD = 0x3603
   MAPI_CREATE_TEMPLATES = 0x3604
   MAPI_DETAILS_TABLE = 0x3605
   MAPI_SEARCH = 0x3607
   MAPI_SELECTABLE = 0x3609
   MAPI_SUBFOLDERS = 0x360A
   MAPI_STATUS = 0x360B
   MAPI_ANR = 0x360C
   MAPI_CONTENTS_SORT_ORDER = 0x360D
   MAPI_CONTAINER_HIERARCHY = 0x360E
   MAPI_CONTAINER_CONTENTS = 0x360F
   MAPI_FOLDER_ASSOCIATED_CONTENTS = 0x3610
   MAPI_DEF_CREATE_DL = 0x3611
   MAPI_DEF_CREATE_MAILUSER = 0x3612
   MAPI_CONTAINER_CLASS = 0x3613
   MAPI_CONTAINER_MODIFY_VERSION = 0x3614
   MAPI_AB_PROVIDER_ID = 0x3615
   MAPI_DEFAULT_VIEW_ENTRYID = 0x3616
   MAPI_ASSOC_CONTENT_COUNT = 0x3617
   MAPI_ATTACHMENT_X400_PARAMETERS = 0x3700
   MAPI_ATTACH_DATA_OBJ = 0x3701
   MAPI_ATTACH_ENCODING = 0x3702
   MAPI_ATTACH_EXTENSION = 0x3703
   MAPI_ATTACH_FILENAME = 0x3704
   MAPI_ATTACH_METHOD = 0x3705
   MAPI_ATTACH_LONG_FILENAME = 0x3707
   MAPI_ATTACH_PATHNAME = 0x3708
   MAPI_ATTACH_RENDERING = 0x3709
   MAPI_ATTACH_TAG = 0x370A
   MAPI_RENDERING_POSITION = 0x370B
   MAPI_ATTACH_TRANSPORT_NAME = 0x370C
   MAPI_ATTACH_LONG_PATHNAME = 0x370D
   MAPI_ATTACH_MIME_TAG = 0x370E
   MAPI_ATTACH_ADDITIONAL_INFO = 0x370F
   MAPI_DISPLAY_TYPE = 0x3900
   MAPI_TEMPLATEID = 0x3902
   MAPI_PRIMARY_CAPABILITY = 0x3904
   MAPI_7BIT_DISPLAY_NAME = 0x39FF
   MAPI_ACCOUNT = 0x3A00
   MAPI_ALTERNATE_RECIPIENT = 0x3A01
   MAPI_CALLBACK_TELEPHONE_NUMBER = 0x3A02
   MAPI_CONVERSION_PROHIBITED = 0x3A03
   MAPI_DISCLOSE_RECIPIENTS = 0x3A04
   MAPI_GENERATION = 0x3A05
   MAPI_GIVEN_NAME = 0x3A06
   MAPI_GOVERNMENT_ID_NUMBER = 0x3A07
   MAPI_BUSINESS_TELEPHONE_NUMBER = 0x3A08
   MAPI_HOME_TELEPHONE_NUMBER = 0x3A09
   MAPI_INITIALS = 0x3A0A
   MAPI_KEYWORD = 0x3A0B
   MAPI_LANGUAGE = 0x3A0C
   MAPI_LOCATION = 0x3A0D
   MAPI_MAIL_PERMISSION = 0x3A0E
   MAPI_MHS_COMMON_NAME = 0x3A0F
   MAPI_ORGANIZATIONAL_ID_NUMBER = 0x3A10
   MAPI_SURNAME = 0x3A11
   MAPI_ORIGINAL_ENTRYID = 0x3A12
   MAPI_ORIGINAL_DISPLAY_NAME = 0x3A13
   MAPI_ORIGINAL_SEARCH_KEY = 0x3A14
   MAPI_POSTAL_ADDRESS = 0x3A15
   MAPI_COMPANY_NAME = 0x3A16
   MAPI_TITLE = 0x3A17
   MAPI_DEPARTMENT_NAME = 0x3A18
   MAPI_OFFICE_LOCATION = 0x3A19
   MAPI_PRIMARY_TELEPHONE_NUMBER = 0x3A1A
   MAPI_BUSINESS2_TELEPHONE_NUMBER = 0x3A1B
   MAPI_MOBILE_TELEPHONE_NUMBER = 0x3A1C
   MAPI_RADIO_TELEPHONE_NUMBER = 0x3A1D
   MAPI_CAR_TELEPHONE_NUMBER = 0x3A1E
   MAPI_OTHER_TELEPHONE_NUMBER = 0x3A1F
   MAPI_TRANSMITABLE_DISPLAY_NAME = 0x3A20
   MAPI_PAGER_TELEPHONE_NUMBER = 0x3A21
   MAPI_USER_CERTIFICATE = 0x3A22
   MAPI_PRIMARY_FAX_NUMBER = 0x3A23
   MAPI_BUSINESS_FAX_NUMBER = 0x3A24
   MAPI_HOME_FAX_NUMBER = 0x3A25
   MAPI_COUNTRY = 0x3A26
   MAPI_LOCALITY = 0x3A27
   MAPI_STATE_OR_PROVINCE = 0x3A28
   MAPI_STREET_ADDRESS = 0x3A29
   MAPI_POSTAL_CODE = 0x3A2A
   MAPI_POST_OFFICE_BOX = 0x3A2B
   MAPI_TELEX_NUMBER = 0x3A2C
   MAPI_ISDN_NUMBER = 0x3A2D
   MAPI_ASSISTANT_TELEPHONE_NUMBER = 0x3A2E
   MAPI_HOME2_TELEPHONE_NUMBER = 0x3A2F
   MAPI_ASSISTANT = 0x3A30
   MAPI_SEND_RICH_INFO = 0x3A40
   MAPI_WEDDING_ANNIVERSARY = 0x3A41
   MAPI_BIRTHDAY = 0x3A42
   MAPI_HOBBIES = 0x3A43
   MAPI_MIDDLE_NAME = 0x3A44
   MAPI_DISPLAY_NAME_PREFIX = 0x3A45
   MAPI_PROFESSION = 0x3A46
   MAPI_PREFERRED_BY_NAME = 0x3A47
   MAPI_SPOUSE_NAME = 0x3A48
   MAPI_COMPUTER_NETWORK_NAME = 0x3A49
   MAPI_CUSTOMER_ID = 0x3A4A
   MAPI_TTYTDD_PHONE_NUMBER = 0x3A4B
   MAPI_FTP_SITE = 0x3A4C
   MAPI_GENDER = 0x3A4D
   MAPI_MANAGER_NAME = 0x3A4E
   MAPI_NICKNAME = 0x3A4F
   MAPI_PERSONAL_HOME_PAGE = 0x3A50
   MAPI_BUSINESS_HOME_PAGE = 0x3A51
   MAPI_CONTACT_VERSION = 0x3A52
   MAPI_CONTACT_ENTRYIDS = 0x3A53
   MAPI_CONTACT_ADDRTYPES = 0x3A54
   MAPI_CONTACT_DEFAULT_ADDRESS_INDEX = 0x3A55
   MAPI_CONTACT_EMAIL_ADDRESSES = 0x3A56
   MAPI_COMPANY_MAIN_PHONE_NUMBER = 0x3A57
   MAPI_CHILDRENS_NAMES = 0x3A58
   MAPI_HOME_ADDRESS_CITY = 0x3A59
   MAPI_HOME_ADDRESS_COUNTRY = 0x3A5A
   MAPI_HOME_ADDRESS_POSTAL_CODE = 0x3A5B
   MAPI_HOME_ADDRESS_STATE_OR_PROVINCE = 0x3A5C
   MAPI_HOME_ADDRESS_STREET = 0x3A5D
   MAPI_HOME_ADDRESS_POST_OFFICE_BOX = 0x3A5E
   MAPI_OTHER_ADDRESS_CITY = 0x3A5F
   MAPI_OTHER_ADDRESS_COUNTRY = 0x3A60
   MAPI_OTHER_ADDRESS_POSTAL_CODE = 0x3A61
   MAPI_OTHER_ADDRESS_STATE_OR_PROVINCE = 0x3A62
   MAPI_OTHER_ADDRESS_STREET = 0x3A63
   MAPI_OTHER_ADDRESS_POST_OFFICE_BOX = 0x3A64
   MAPI_STORE_PROVIDERS = 0x3D00
   MAPI_AB_PROVIDERS = 0x3D01
   MAPI_TRANSPORT_PROVIDERS = 0x3D02
   MAPI_DEFAULT_PROFILE = 0x3D04
   MAPI_AB_SEARCH_PATH = 0x3D05
   MAPI_AB_DEFAULT_DIR = 0x3D06
   MAPI_AB_DEFAULT_PAB = 0x3D07
   MAPI_FILTERING_HOOKS = 0x3D08
   MAPI_SERVICE_NAME = 0x3D09
   MAPI_SERVICE_DLL_NAME = 0x3D0A
   MAPI_SERVICE_ENTRY_NAME = 0x3D0B
   MAPI_SERVICE_UID = 0x3D0C
   MAPI_SERVICE_EXTRA_UIDS = 0x3D0D
   MAPI_SERVICES = 0x3D0E
   MAPI_SERVICE_SUPPORT_FILES = 0x3D0F
   MAPI_SERVICE_DELETE_FILES = 0x3D10
   MAPI_AB_SEARCH_PATH_UPDATE = 0x3D11
   MAPI_PROFILE_NAME = 0x3D12
   MAPI_IDENTITY_DISPLAY = 0x3E00
   MAPI_IDENTITY_ENTRYID = 0x3E01
   MAPI_RESOURCE_METHODS = 0x3E02
   MAPI_RESOURCE_TYPE = 0x3E03
   MAPI_STATUS_CODE = 0x3E04
   MAPI_IDENTITY_SEARCH_KEY = 0x3E05
   MAPI_OWN_STORE_ENTRYID = 0x3E06
   MAPI_RESOURCE_PATH = 0x3E07
   MAPI_STATUS_STRING = 0x3E08
   MAPI_X400_DEFERRED_DELIVERY_CANCEL = 0x3E09
   MAPI_HEADER_FOLDER_ENTRYID = 0x3E0A
   MAPI_REMOTE_PROGRESS = 0x3E0B
   MAPI_REMOTE_PROGRESS_TEXT = 0x3E0C
   MAPI_REMOTE_VALIDATE_OK = 0x3E0D
   MAPI_CONTROL_FLAGS = 0x3F00
   MAPI_CONTROL_STRUCTURE = 0x3F01
   MAPI_CONTROL_TYPE = 0x3F02
   MAPI_DELTAX = 0x3F03
   MAPI_DELTAY = 0x3F04
   MAPI_XPOS = 0x3F05
   MAPI_YPOS = 0x3F06
   MAPI_CONTROL_ID = 0x3F07
   MAPI_INITIAL_DETAILS_PANE = 0x3F08
   MAPI_ID_SECURE_MIN = 0x67F0
   MAPI_ID_SECURE_MAX = 0x67FF


   def __init__(self, attr_type, name,data):
      self.attr_type = attr_type
      self.name = name
      self.data = data


class TNEFObject:
   "a TNEF object that may contain a property and an attachment"

   def __init__(self, level,name,type,data, checksum_ok):
      self.level = level
      self.type = type
      self.name = name
      self.data = data
      self.good_checksum = checksum_ok


class TNEFAttachment:
   "a TNEF attachment"

   SZMAPI_UNSPECIFIED    = 0x0000 # MAPI Unspecified
   SZMAPI_NULL           = 0x0001 # MAPI null property
   SZMAPI_SHORT          = 0x0002 # MAPI short (signed 16 bits)
   SZMAPI_INT            = 0x0003 # MAPI integer (signed 32 bits)
   SZMAPI_FLOAT          = 0x0004 # MAPI float (4 bytes)
   SZMAPI_DOUBLE         = 0x0005 # MAPI double
   SZMAPI_CURRENCY       = 0x0006 # MAPI currency (64 bits)
   SZMAPI_APPTIME        = 0x0007 # MAPI application time
   SZMAPI_ERROR          = 0x000a # MAPI error (32 bits)
   SZMAPI_BOOLEAN        = 0x000b # MAPI boolean (16 bits)
   SZMAPI_OBJECT         = 0x000d # MAPI embedded object
   SZMAPI_INT8BYTE       = 0x0014 # MAPI 8 byte signed int
   SZMAPI_STRING         = 0x001e # MAPI string
   SZMAPI_UNICODE_STRING = 0x001f # MAPI unicode-string (null terminated)
   SZMAPI_SYSTIME        = 0x0040 # MAPI time (64 bits)
   SZMAPI_CLSID          = 0x0048 # MAPI OLE GUID
   SZMAPI_BINARY         = 0x0102 # MAPI binary
   SZMAPI_BEATS_THE_HELL_OUTTA_ME = 0x0033

   def __init__(self):
      self.mapi_attrs = []

   def long_filename(self):
      atname = TNEFMAPI_Attribute.MAPI_ATTACH_LONG_FILENAME
      attr = None
      for a in self.mapi_attrs:
         if a.name == atname:
            attr = a
            break

      if attr is not None:
         fn = str(attr.data).replace('0','')
      else:
         fn = self.name

      return fn.split('\\')[-1]


   def add_attr(self, attribute):
      #debug("Attachment attr name: #{sprintf('0x%4.4x',attribute.name)}")
      if attribute == TNEF.ATTATTACHMODIFYDATE:
         debug("No date support yet!")
      elif attribute == TNEF.ATTATTACHMENT:
         self.mapi_attrs += decode_mapi(attribute.data)
      elif attribute == TNEF.ATTATTACHTITLE:
         self.name = attribute.data
      elif attribute == TNEF.ATTATTACHDATA:
         self.data = attribute.data
      else:
         debug("Unknown attribute name: %s" % attribute)


   def decode_mapi(self, data):
      #debug("DECODE MAPI UNFINISHED!!")
      attrs = []
      offset = 0
      num_properties = bytes_to_int(data[offset,4]); offset += 4

      for i in range(num_properties):

         if offset >= data.length:
            print "Skipping property '%i'" % i
            continue

         attr_type = bytes_to_int(data[offset,2]); offset += 2
         attr_name = bytes_to_int(data[offset,2]); offset += 2

         attr_data = nil

         if attr_type == SZMAPI_SHORT:
            attr_data = data[offset,2]; offset += 2
         elif attr_type in (SZMAPI_INT, SZMAPI_FLOAT, SZMAPI_ERROR, SZMAPI_BOOLEAN):
            attr_data = data[offset,4]; offset += 4
         elif attr_type in (SZMAPI_DOUBLE, SZMAPI_APPTIME, SZMAPI_CURRENCY, SZMAPI_INT8BYTE, SZMAPI_SYSTIME):
            attr_data = data[offset,8]; offset += 8
         elif attr_type == SZMAPI_CLSID:
            attr_data = data[offset,16]; offset += 16
         elif attr_data in (SZMAPI_STRING, SZMAPI_UNICODE_STRING, SZMAPI_OBJECT, SZMAPI_BINARY, SZMAPI_UNSPECIFIED):
            #debug sprintf('data[%i,8] = %2.2x%2.2x %2.2x%2.2x %2.2x%2.2x '+
            #              '%2.2x%2.2x',offset,
            #              data[offset],
            #              data[offset+1],
            #              data[offset+2],
            #              data[offset+3],
            #              data[offset+4],
            #              data[offset+5],
            #              data[offset+6],
            #              data[offset+7],
            #              data[offset+8])
            num_vals = bytes_to_int(data[offset,4]); offset += 4

            #debug ("num_vals: #{sprintf('0x%2.2x',num_vals)}")
            attr_data = []

            for j in range(num_vals):
               length = bytes_to_int(data[offset,4]) ; offset += 4
               q,r = length.divmod(4)
               if r != 0:
                  length += (4-r)
               #debug ("len: #{len}")

               # I really don't know about this part!  I'm making it up.
               #if len == 0
               #  attr_data[j] = data[offset,data.length]
               #  offset = data.length
               #  debug attr_data[j]
               #else
               attr_data[j] = data[offset,length]; offset += length
               #end
         else:
            debug("## Unknown MAPI type 0x%s" % attr_type)
            debug("attr_type: 0x%s" % attr_type)
            debug("attr_name: 0x%s" % attr_name)
            break

         attr = TNEFMAPI_Attribute.new ( attr_type, attr_name, attr_data)
         attrs[i] = attr

      return attrs


class TNEF:
   "main decoder class - start by using this"

   TNEF_SIGNATURE = 0x223e9f78
   LVL_MESSAGE = 0x01
   LVL_ATTACHMENT = 0x02

   ATTOWNER                        = 0x0000 # Owner
   ATTSENTFOR                      = 0x0001 # Sent For
   ATTDELEGATE                     = 0x0002 # Delegate
   ATTDATESTART                    = 0x0006 # Date Start
   ATTDATEEND                      = 0x0007 # Date End
   ATTAIDOWNER                     = 0x0008 # Owner Appointment ID
   ATTREQUESTRES                   = 0x0009 # Response Requested.
   ATTFROM                         = 0x8000 # From
   ATTSUBJECT                      = 0x8004 # Subject
   ATTDATESENT                     = 0x8005 # Date Sent
   ATTDATERECD                     = 0x8006 # Date Recieved
   ATTMESSAGESTATUS                = 0x8007 # Message Status
   ATTMESSAGECLASS                 = 0x8008 # Message Class
   ATTMESSAGEID                    = 0x8009 # Message ID
   ATTPARENTID                     = 0x800a # Parent ID
   ATTCONVERSATIONID               = 0x800b # Conversation ID
   ATTBODY                         = 0x800c # Body
   ATTPRIORITY                     = 0x800d # Priority
   ATTATTACHDATA                   = 0x800f # Attachment Data
   ATTATTACHTITLE                  = 0x8010 # Attachment File Name
   ATTATTACHMETAFILE               = 0x8011 # Attachment Meta File
   ATTATTACHCREATEDATE             = 0x8012 # Attachment Creation Date
   ATTATTACHMODIFYDATE             = 0x8013 # Attachment Modification Date
   ATTDATEMODIFY                   = 0x8020 # Date Modified
   ATTATTACHTRANSPORTFILENAME      = 0x9001 # Attachment Transport Filename
   ATTATTACHRENDDATA               = 0x9002 # Attachment Rendering Data
   ATTMAPIPROPS                    = 0x9003 # MAPI Properties
   ATTRECIPTABLE                   = 0x9004 # Recipients
   ATTATTACHMENT                   = 0x9005 # Attachment
   ATTTNEFVERSION                  = 0x9006 # TNEF Version
   ATTOEMCODEPAGE                  = 0x9007 # OEM Codepage
   ATTORIGNINALMESSAGECLASS        = 0x9008 # Original Message Class

   codes = {
      ATTOWNER                        :  "Owner",
      ATTSENTFOR                      :  "Sent For",
      ATTDELEGATE                     :  "Delegate",
      ATTDATESTART                    :  "Date Start",
      ATTDATEEND                      :  "Date End",
      ATTAIDOWNER                     :  "Owner Appointment ID",
      ATTREQUESTRES                   :  "Response Requested",
      ATTFROM                         :  "From",
      ATTSUBJECT                      :  "Subject",
      ATTDATESENT                     :  "Date Sent",
      ATTDATERECD                     :  "Date Received",
      ATTMESSAGESTATUS                :  "Message Status",
      ATTMESSAGECLASS                 :  "Message Class",
      ATTMESSAGEID                    :  "Message ID",
      ATTPARENTID                     :  "Parent ID",
      ATTCONVERSATIONID               :  "Conversation ID",
      ATTBODY                         :  "Body",
      ATTPRIORITY                     :  "Priority",
      ATTATTACHDATA                   :  "Attachment Data",
      ATTATTACHTITLE                  :  "Attachment File Name",
      ATTATTACHMETAFILE               :  "Attachment Meta File",
      ATTATTACHCREATEDATE             :  "Attachment Creation Date",
      ATTATTACHMODIFYDATE             :  "Attachment Modification Date",
      ATTDATEMODIFY                   :  "Date Modified",
      ATTATTACHTRANSPORTFILENAME      :  "Attachment Transport Filename",
      ATTATTACHRENDDATA               :  "Attachment Rendering Data",
      ATTMAPIPROPS                    :  "MAPI Properties",
      ATTRECIPTABLE                   :  "Recipients",
      ATTATTACHMENT                   :  "Attachment",
      ATTTNEFVERSION                  :  "TNEF Version",
      ATTOEMCODEPAGE                  :  "OEM Codepage",
      ATTORIGNINALMESSAGECLASS        :  "Original Message Class"
   }

   def __init__(self, data, do_checksum = True):
      self.signature = bytes_to_int(data[0:4])
      #debug("Signature: #{self.signature}, normal #{TNEF_SIGNATURE}")
      self.key = bytes_to_int(data[4:6])
      #debug ("Key: #{sprintf('0x%2.2x',key)}")
      self.objects = []
      self.attachments = []
      offset = 6

      while (offset < len(data)):
         length, obj = self.decode_object(data[offset: offset+len(data)], do_checksum)
         offset += length
         self.objects.append(obj)
         #debug("LEVEL: #{object.level}")
         if obj.name == TNEF.ATTATTACHRENDDATA:
            attachment = TNEFAttachment()
            if obj.level == LVL_ATTACHMENT:
               attachment.add_attr(obj)
            self.attachments.append(attachment)


   def decode_object(self, data, do_checksum = True):
      "decode TNEF objects from the byte 'stream'"
      offset = 0
      att_lvl = bytes_to_int(data[offset: offset+1]); offset += 1
      att_name = bytes_to_int(data[offset:offset+2]); offset += 2
      att_type = bytes_to_int(data[offset:offset+2]); offset += 2
      att_length = bytes_to_int(data[offset:offset+4]); offset += 4
      att_data = data[offset:offset+att_length]; offset += att_length
      att_checksum = bytes_to_int(data[offset:offset+2]); offset += 2

      if do_checksum:
         calc_checksum = self.checksum(att_data)
         if calc_checksum != att_checksum:
            debug("Checksum: %s != %s" % (calc_checksum, att_checksum))
      else:
         #debug ("Skipping checksum for performance")
         calc_checksum = att_checksum

      checksum_ok = calc_checksum == att_checksum
      object = TNEFObject(att_lvl, att_name, att_type, att_data, checksum_ok)
      return offset, object


   def checksum(self, data):
      "calculate a checksum for the TNEF data"
      sum = 0
      for byte in data:
         sum = (sum + ord(byte)) % 65536
      return sum


if __name__ == "__main__":

   filename = "winmail.dat"
   T = TNEF(open(filename).read())
   print "Key:", T.key
   print "Objects:"
   for o in T.objects:
      print TNEF.codes[o.name]
   print "Attachments:", T.attachments
