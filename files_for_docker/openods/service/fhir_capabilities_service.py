from openods import constants
from openods import log_utils
JSON = """{"resourceType":"CapabilityStatement","url":"%s","version":"%s","name":"ODSAPI-CapabilityStatement-1","status":"draft","date":"2018-02-01","publisher":"NHS Digital","contact":[{"name":"National Helpdesk Exeter","telecom":[{"system":"email","value":"exeter.helpdesk@nhs.net","use":"work"},{"system":"phone","value":"0300 303 4034","use":"work"}]}],"description":"An API for retrieving organisation data from the NHS Digital Organisation Data Service.","copyright":"Copyright © 2017 NHS Digital","kind":"instance","instantiates":["https://fhir.nhs.uk/STU3/CapabilityStatement/ODSAPI-CapabilityStatement-1"],"fhirVersion":"3.0.1","acceptUnknown":"no","format":["application/fhir+xml","application/fhir+json"],"implementationGuide":["https://developer.nhs.uk/apis/ods/"],"profile":[{"reference":"https://fhir.nhs.uk/STU3/StructureDefinition/ODSAPI-Organization-1"},{"reference":"https://fhir.nhs.uk/STU3/StructureDefinition/ODSAPI-ActivePeriod-1"},{"reference":"https://fhir.nhs.uk/STU3/StructureDefinition/Extension-ODSAPI-ActivePeriod-1"},{"reference":"https://fhir.nhs.uk/STU3/StructureDefinition/Extension-ODSAPI-OrganizationRole-1"},{"reference":"https://fhir.nhs.uk/STU3/StructureDefinition/Extension-ODSAPI-UPRN-1"},{"reference":"https://fhir.nhs.uk/STU3/StructureDefinition/Extension-ODSAPI-DateType-1"}],"rest":[{"mode":"server","security":{"cors":true},"resource":[{"extension":[{"url":"http://hl7.org/fhir/StructureDefinition/capabilitystatement-search-parameter-combination","extension":[{"url":"required","valueString":"ods-org-primaryRole"},{"url":"required","valueString":"ods-org-role"}]}],"type":"Organization","profile":{"reference":"https://fhir.nhs.uk/STU3/StructureDefinition/ODSAPI-Organization-1"},"interaction":[{"code":"read"},{"code":"search-type"}],"versioning":"no-version","readHistory":false,"updateCreate":false,"conditionalCreate":false,"conditionalRead":"not-supported","conditionalUpdate":false,"conditionalDelete":"not-supported","searchParam":[{"name":"_id","type":"token"},{"name":"_lastUpdated","type":"date"},{"name":"_count","type":"number"},{"name":"_summary","type":"token"},{"name":"identifier","type":"token"},{"name":"name","type":"string"},{"name":"active","type":"token"},{"name":"address-city","type":"string"},{"name":"address-postalcode","type":"string"},{"name":"ods-org-role","definition":"https://fhir.nhs.uk/STU3/SearchParameter/ODSAPI-OrganizationRole-Role-1","type":"token"},{"name":"ods-org-primaryRole","definition":"https://fhir.nhs.uk/STU3/SearchParameter/ODSAPI-OrganizationRole-PrimaryRole-1","type":"token"}]},{"type":"CodeSystem","interaction":[{"code":"read"}],"versioning":"no-version","readHistory":false,"updateCreate":false,"conditionalCreate":false,"conditionalRead":"not-supported","conditionalUpdate":false,"conditionalDelete":"not-supported","searchParam":[{"name":"url","type":"string","documentation":"The logical URL for the CodeSystem"}]}]}]}"""

XML = """<?xml version='1.0' encoding='UTF-8'?><CapabilityStatement xmlns="http://hl7.org/fhir"><url value="%s" /><version value="%s" /><name value="ODSAPI-CapabilityStatement-1" /><status value="draft" /><date value="2018-02-01" /><publisher value="NHS Digital" /><contact><name value="National Helpdesk Exeter" /><telecom><system value="email" /><value value="exeter.helpdesk@nhs.net" /><use value="work" /></telecom><telecom><system value="phone" /><value value="0300 303 4034" /><use value="work" /></telecom></contact><description value="An API for retrieving organisation data from the NHS Digital Organisation Data Service." /><copyright value="Copyright © 2017 NHS Digital" /><kind value="instance" /><instantiates value="https://fhir.nhs.uk/STU3/CapabilityStatement/ODSAPI-CapabilityStatement-1" /><fhirVersion value="3.0.1" /><acceptUnknown value="no" /><format value="application/fhir+xml" /><format value="application/fhir+json" /><implementationGuide value="https://developer.nhs.uk/apis/ods/" /><profile><reference value="https://fhir.nhs.uk/STU3/StructureDefinition/ODSAPI-Organization-1" /></profile><profile><reference value="https://fhir.nhs.uk/STU3/StructureDefinition/ODSAPI-ActivePeriod-1" /></profile><profile><reference value="https://fhir.nhs.uk/STU3/StructureDefinition/Extension-ODSAPI-ActivePeriod-1" /></profile><profile><reference value="https://fhir.nhs.uk/STU3/StructureDefinition/Extension-ODSAPI-OrganizationRole-1" /></profile><profile><reference value="https://fhir.nhs.uk/STU3/StructureDefinition/Extension-ODSAPI-UPRN-1" /></profile><profile><reference value="https://fhir.nhs.uk/STU3/StructureDefinition/Extension-ODSAPI-DateType-1" /></profile><rest><mode value="server" /><security><cors value="true" /></security><resource><extension url="http://hl7.org/fhir/StructureDefinition/capabilitystatement-search-parameter-combination"><extension url="required"><valueString value="ods-org-primaryRole" /></extension><extension url="required"><valueString value="ods-org-role" /></extension></extension><type value="Organization" /><profile><reference value="https://fhir.nhs.uk/STU3/StructureDefinition/ODSAPI-Organization-1" /></profile><interaction><code value="read" /></interaction><interaction><code value="search-type" /></interaction><versioning value="no-version" /><readHistory value="false" /><updateCreate value="false" /><conditionalCreate value="false" /><conditionalRead value="not-supported" /><conditionalUpdate value="false" /><conditionalDelete value="not-supported" /><searchParam><name value="_id" /><type value="token" /></searchParam><searchParam><name value="_lastUpdated" /><type value="date" /></searchParam><searchParam><name value="_count" /><type value="number" /></searchParam><searchParam><name value="_summary" /><type value="token" /></searchParam><searchParam><name value="identifier" /><type value="token" /></searchParam><searchParam><name value="name" /><type value="string" /></searchParam><searchParam><name value="active" /><type value="token" /></searchParam><searchParam><name value="address-city" /><type value="string" /></searchParam><searchParam><name value="address-postalcode" /><type value="string" /></searchParam><searchParam><name value="ods-org-role" /><definition value="https://fhir.nhs.uk/STU3/SearchParameter/ODSAPI-OrganizationRole-Role-1" /><type value="token" /></searchParam><searchParam><name value="ods-org-primaryRole" /><definition value="https://fhir.nhs.uk/STU3/SearchParameter/ODSAPI-OrganizationRole-PrimaryRole-1" /><type value="token" /></searchParam></resource><resource><type value="CodeSystem" /><interaction><code value="read" /></interaction><versioning value="no-version" /><readHistory value="false" /><updateCreate value="false" /><conditionalCreate value="false" /><conditionalRead value="not-supported" /><conditionalUpdate value="false" /><conditionalDelete value="not-supported" /><searchParam><name value="url" /><type value="string" /><documentation value="The logical URL for the CodeSystem" /></searchParam></resource></rest></CapabilityStatement>"""

def get_fhir_capabilities(format, request_url, request_id):
    log_utils.log_layer_entry(constants.SERVICE, request_id )

    if format == constants.JSON:
        response_body = JSON % (request_url, "1.1.0")

    else:
        response_body = XML % (request_url, "1.1.0")

    log_utils.log_layer_exit(constants.SERVICE, request_id)

    return response_body