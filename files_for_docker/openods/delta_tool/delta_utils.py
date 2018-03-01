
import datetime
import psycopg2
import threading
import os
import smtplib

from lxml import etree as xml_tree_parser

from pathlib import Path

from tqdm import tqdm
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from openods.delta_tool.models.Organisation import Organisation
from openods.delta_tool.models.Address import Address
from openods.delta_tool.models.Contact import Contact
from openods.delta_tool.models.Relationship import Relationship
from openods.delta_tool.models.Role import Role
from openods.delta_tool.models.Successor import Successor
from openods.delta_tool.models.base import Base
from openods.delta_tool.models.Version import Version
from openods.delta_tool.models.Setting import Setting
from openods.delta_tool.models.CodeSystem import CodeSystem
from openods import connection
from openods import constants
from openods import app
from openods.handlers import upload_file_handler

from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from urllib.parse import urlparse


def convert_string_to_date(string):
    return datetime.datetime.strptime(string, '%Y-%m-%d')


def create_organisation(organisation, code):
    new_org = Organisation()
    new_org.odscode = code
    new_org.name = organisation.find('Name').text
    new_org.status = organisation.find('Status').attrib.get('value')
    new_org.record_class = organisation.attrib.get('orgRecordClass')
    new_org.last_changed = organisation.find('LastChangeDate').attrib.get('value')
    new_org.ref_only = bool(organisation.attrib.get('refOnly'))
    for date in organisation.findall('Date'):
        if date.find('Type').attrib.get('value') == 'Legal':

            try:
                new_org.legal_start_date = \
                    convert_string_to_date(date.find('Start').attrib.get('value'))
            except:
                pass

            try:
                new_org.legal_end_date = \
                    convert_string_to_date(date.find('End').attrib.get('value'))
            except:
                pass

        elif date.find('Type').attrib.get('value') == 'Operational':
            try:
                new_org.operational_start_date = \
                    convert_string_to_date(date.find('Start').attrib.get('value'))
            except:
                pass

            try:
                new_org.operational_end_date = \
                    convert_string_to_date(date.find('End').attrib.get('value'))
            except:
                pass

    return new_org

def create_address(organisation, code):
    location = organisation.find('GeoLoc/Location')

    new_address = Address()

    try:
        new_address.org_odscode = code
    except AttributeError:
        pass

    try:
        new_address.address_line1 = location.find('AddrLn1').text
    except AttributeError:
        pass

    try:
        new_address.address_line2 = location.find('AddrLn2').text
    except AttributeError:
        pass

    try:
        new_address.address_line3 = location.find('AddrLn3').text
    except AttributeError:
        pass

    try:
        new_address.town = location.find('Town').text
    except AttributeError:
        pass

    try:
        new_address.county = location.find('County').text
    except AttributeError:
        pass

    try:
        new_address.post_code = location.find('PostCode').text
    except AttributeError:
        pass

    try:
        new_address.country = location.find('Country').text
    except AttributeError:
        pass

    try:
        new_address.uprn = location.find('UPRN').text
    except AttributeError:
        pass

    return new_address

def create_contacts(organisation, code):
    contacts_xml = organisation.find('Contacts')
    new_contacts = []

    if contacts_xml is not None:

        for idx, contact in enumerate(contacts_xml):
            new_contact = Contact()
            new_contact.org_odscode = code
            new_contact.type = contact.attrib.get('type')
            new_contact.value = contact.attrib.get('value')

            new_contacts.append(new_contact)

    return new_contacts

def create_relationships(organisation, code):
    relationships_xml = organisation.find('Rels')
    new_relationships = []

    if relationships_xml is not None:

        for idx, relationship in enumerate(relationships_xml):

            new_relationship = Relationship()

            new_relationship.code = relationship.attrib.get('id')
            new_relationship.target_odscode = relationship.find('Target/OrgId').attrib.get('extension')
            new_relationship.org_odscode = code

            for date in relationship.findall('Date'):
                if date.find('Type').attrib.get('value') == 'Legal':
                    try:
                        new_relationship.legal_start_date = \
                            convert_string_to_date(date.find('Start').attrib.get('value'))
                    except:
                        pass
                    try:
                        new_relationship.legal_end_date = \
                            convert_string_to_date(date.find('End').attrib.get('value'))
                    except:
                        pass

                elif date.find('Type').attrib.get('value') == 'Operational':
                    try:
                        new_relationship.operational_start_date = \
                            convert_string_to_date(date.find('Start').attrib.get('value'))
                    except:
                        pass
                    try:
                        new_relationship.operational_end_date = \
                            convert_string_to_date(date.find('End').attrib.get('value'))
                    except:
                        pass

            new_relationship.status = relationship.find(
                'Status').attrib.get('value')
            new_relationship.unique_id = relationship.attrib.get(
                'uniqueRelId')

            try:
                new_relationship.target_primary_role_code = \
                    relationship.find('Target/PrimaryRoleId').attrib.get('id')
            except AttributeError:
                pass

            try:
                new_relationship.target_unique_role_id = \
                    relationship.find('Target/PrimaryRoleId').attrib.get('uniqueRoleId')
            except AttributeError:
                pass

            new_relationships.append(new_relationship)

    return new_relationships

def create_roles(organisation, code):
    roles_xml = organisation.find('Roles')
    new_roles = []

    for idx, role in enumerate(roles_xml):

        new_role = Role()

        new_role.org_odscode = code
        new_role.code = role.attrib.get('id')
        new_role.primary_role = bool(role.attrib.get('primaryRole'))
        new_role.unique_id = role.attrib.get('uniqueRoleId')
        new_role.status = role.find('Status').attrib.get('value')

        # Add Operational and Legal start/end dates if present
        for date in role.findall('Date'):
            if date.find('Type').attrib.get('value') == 'Legal':
                try:
                    new_role.legal_start_date = \
                        convert_string_to_date(date.find('Start').attrib.get('value'))
                except:
                    pass
                try:
                    new_role.legal_end_date = \
                        convert_string_to_date(date.find('End').attrib.get('value'))
                except:
                    pass

            elif date.find('Type').attrib.get('value') == 'Operational':
                try:
                    new_role.operational_start_date = \
                        convert_string_to_date(date.find('Start').attrib.get('value'))
                except:
                    pass
                try:
                    new_role.operational_end_date = \
                        convert_string_to_date(date.find('End').attrib.get('value'))
                except:
                    pass

        new_roles.append(new_role)

    return new_roles

def create_successors(organisation, code):
    new_successors = []

    for idx, succ in enumerate(organisation.findall(
            'Succs/Succ')):

        new_successor = Successor()

        try:
            new_successor.unique_id = succ.attrib.get('uniqueSuccId')
        except AttributeError:
            pass

        try:
            new_successor.org_odscode = code
        except AttributeError:
            pass

        try:
            new_successor.legal_start_date = \
                convert_string_to_date(succ.find('Date/Start').attrib.get('value'))
        except AttributeError:
            pass

        try:
            new_successor.type = \
                succ.find('Type').text
        except AttributeError:
            pass

        try:
            new_successor.target_odscode = \
                succ.find('Target/OrgId').attrib.get('extension')
        except AttributeError:
            pass

        try:
            new_successor.target_primary_role_code = \
                succ.find('Target/PrimaryRoleId').attrib.get('id')
        except AttributeError:
            pass

        try:
            new_successor.target_unique_role_id = \
                succ.find('Target/PrimaryRoleId').attrib.get('uniqueRoleId')
        except AttributeError:
            pass

        new_successors.append(new_successor)

    return new_successors

def create_version(ods_xml_data):
    version = Version()

    version.file_version = ods_xml_data.find(
        './Manifest/Version').attrib.get('value')
    version.publication_date = ods_xml_data.find(
        './Manifest/PublicationDate').attrib.get('value')
    version.publication_type = ods_xml_data.find(
        './Manifest/PublicationType').attrib.get('value')
    version.publication_seqno = ods_xml_data.find(
        './Manifest/PublicationSeqNum').attrib.get('value')
    version.publication_source = ods_xml_data.find(
        './Manifest/PublicationSource').attrib.get('value')
    version.file_creation_date = ods_xml_data.find(
        './Manifest/FileCreationDateTime').attrib.get('value')
    version.import_timestamp = datetime.datetime.now()
    version.record_count = ods_xml_data.find(
        './Manifest/RecordCount').attrib.get('value')
    version.content_description = ods_xml_data.find(
        './Manifest/ContentDescription').attrib.get('value')

    return version

def create_settings():
    setting = Setting()
    setting.key = 'schema_version'
    setting.value = constants.SCHEMA_VERSION
    return setting

def create_codesystems(ods_xml_data, session):
    # code_system_types = [
    #     './CodeSystems/CodeSystem[@name="OrganisationRelationship"]',
    #     './CodeSystems/CodeSystem[@name="OrganisationRecordClass"]',
    #     './CodeSystems/CodeSystem[@name="OrganisationRole"]']
    code_system_types = ['OrganisationRelationship',
                         'OrganisationRecordClass',
                         'OrganisationRole']

    for code_system_type in code_system_types:
        relationships = ods_xml_data.find('./CodeSystems/CodeSystem[@name="' + code_system_type + '"]')
        # relationship_types = {}

        # enumerate the iter as it doesn't provide an index which we need
        for idx, relationship in enumerate(relationships.findall('concept')):
            codesystem = CodeSystem()

            relationship_id = relationship.attrib.get('id')
            display_name = relationship.attrib.get('displayName')

            cs = session.query(CodeSystem).filter_by(id=relationship_id, name=code_system_type).first()
            if cs is not None:
                session.delete(cs)

            codesystem.id = relationship_id
            codesystem.name = code_system_type
            codesystem.displayname = display_name

            session.add(codesystem)

        session.commit()


def apply_changes(filename):
    print("applying changes from XML file to an existing DB")

    # ods_xml_data = xml_tree_parser.parse(xml_file_path)
    ods_xml_data = upload_file_handler.get_xml_data(filename)

    engine = create_engine("postgresql://markharrison:openods@localhost/import_test_backup",
                              isolation_level="READ UNCOMMITTED")

    # Create the SQLAlchemy session
    Session = sessionmaker(bind=engine)
    session = Session()

    metadata = Base.metadata
    metadata.create_all(engine)

    # ver = session.query(Version).first()
    # session.delete(ver)
    version = create_version(ods_xml_data)
    session.add(version)

    # old_settings = session.query(Setting).first()
    # session.delete(old_settings)
    # new_settings = create_settings()
    # session.add(new_settings)

    session.commit()

    for idx, organisation in tqdm(enumerate(ods_xml_data.findall(
           '.Organisations/Organisation'))):
        code = organisation.find('OrgId').attrib.get('extension')

        org = session.query(Organisation).filter_by(odscode=code).first()
        session.delete(org)
        new_org = create_organisation(organisation, code)
        session.add(new_org)

        address = session.query(Address).filter_by(org_odscode=code).first()
        session.delete(address)
        new_address = create_address(organisation, code)
        session.add(new_address)

        for contact in session.query(Contact).filter_by(org_odscode=code).all():
            session.delete(contact)
        for new_contact in create_contacts(organisation, code):
            session.add(new_contact)

        for relationship in session.query(Relationship).filter_by(org_odscode=code).all():
            session.delete(relationship)
        for new_relationship in create_relationships(organisation, code):
            session.add(new_relationship)

        for role in session.query(Role).filter_by(org_odscode=code).all():
            session.delete(role)
        for new_role in create_roles(organisation, code):
            session.add(new_role)

        for successor in session.query(Successor).filter_by(org_odscode=code).all():
            session.delete(successor)
        for new_successor in create_roles(organisation, code):
            session.add(new_successor)

        session.commit()

    create_codesystems(ods_xml_data, session)

    print("END of applying changes.")



def perform_database_update(filename):
    # valid = validate_xml_against_schema(xml_file_path)
    valid = validate_xml_against_schema(filename)

    if not valid:
        print("DATA FILE NOT SCHEMA VALID")
        return
    else:
        print("DATA FILE IS SCHEMA VALID")

    db_names = get_pg_databases()

    db_names_list = []
    for dict in db_names:
        db = dict['datname']
        db_names_list.append(db)

    required_dbs = [constants.LIVE_DATABASE, constants.BACKUP_DATABASE]
    for required_db in required_dbs:
        if required_db not in db_names_list:
            print("MISSING " + required_db + ". Can't do upload.")
            return

    ct = threading.current_thread()
    ctName = ct.getName()
    print("current thread name = " + ctName)

    threads_to_run_file = Path(constants.FILE_LOCATION_PATH + constants.THREADS_TO_RUN)
    if not threads_to_run_file.is_file():
        print("NOT CONTINUING WITH THIS THREAD AS THIS UPLOAD HAS BEEN CANCELLED")
        return

    file = open(constants.FILE_LOCATION_PATH + constants.THREADS_TO_RUN, 'r')
    line = file.readline()
    file.close()

    thread_name = line.split(':')[0]

    if thread_name != ctName:
        print("NOT CONTINUING WITH THIS THREAD AS THE UPLOAD ID DOESN'T MATCH THE EXPECTED ONE")
        return

    os.remove(constants.FILE_LOCATION_PATH + constants.THREADS_TO_RUN)

    # Apply changes to backup
    apply_changes(filename)

    connection.close_connection_pool()

    if constants.ARCHIVED_DATABASE in db_names_list:
        delete_db(constants.ARCHIVED_DATABASE)

    clone_db(constants.BACKUP_DATABASE, constants.NEW_BACKUP_DATABASE)

    rename_db(constants.LIVE_DATABASE, constants.ARCHIVED_DATABASE)

    rename_db(constants.BACKUP_DATABASE, constants.LIVE_DATABASE)

    url = urlparse(app.config['DATABASE_URL'])
    connection.init_connection_pool(url, constants.CONNECTION_POOL_SIZE)

    rename_db(constants.NEW_BACKUP_DATABASE, constants.BACKUP_DATABASE)

    # send_email(constants.SENDING_EMAIL, constants.RECIPIENT_EMAIL, "Delta Upload Results", "THIS WORKED!")


# def validate_xml_against_schema(filename):
#     ods_xml_data = xml_tree_parser.parse(constants.FILE_LOCATION_PATH + filename)
#     ods_xml_schema_file = xml_tree_parser.parse(constants.FILE_LOCATION_PATH + constants.CURRENT_SCHEMA_FILE)
#     ods_xml_schema = xml_tree_parser.XMLSchema(ods_xml_schema_file)
#     valid = ods_xml_schema.validate(ods_xml_data)
#     return valid

def validate_xml_against_schema(filename):
    ods_xml_data = upload_file_handler.get_xml_data(filename)
    ods_xml_schema_file = upload_file_handler.get_xml_schema(constants.CURRENT_SCHEMA_FILE)
    ods_xml_schema = xml_tree_parser.XMLSchema(ods_xml_schema_file)
    valid = ods_xml_schema.validate(ods_xml_data)
    return valid


def get_pg_databases():

    sql = "SELECT datname FROM pg_database"

    return execute_isolated_postgres_query(sql)

def clone_db(target_db_name, clone_db_name):

    kill_db_connections(target_db_name)

    create_clone_sql = 'CREATE DATABASE {0} TEMPLATE {1};'.format(clone_db_name, target_db_name)

    execute_isolated_postgres_statement(create_clone_sql)


def kill_db_connections(target_db_name):
    kill_connection_sql = '''SELECT pg_terminate_backend(pg_stat_activity.pid)
                             FROM pg_stat_activity
                             WHERE pg_stat_activity.datname = '{}'
                             AND pid <> pg_backend_pid();'''.format(target_db_name)

    # conn = connection.get_connection('postgres', 'postgres', '', 'dev.ods.cis.spine2.ncrs.nhs.uk', 5432)
    conn = connection.get_connection('postgres', 'postgres', '', 'localhost', 5432)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute(kill_connection_sql)
    conn.close()

def execute_isolated_postgres_statement(sql):
    # conn = connection.get_connection('postgres', 'postgres', '', 'dev.ods.cis.spine2.ncrs.nhs.uk', 5432)
    conn = connection.get_connection('postgres', 'postgres', '', 'localhost', 5432)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute(sql)
    conn.close()

def execute_isolated_postgres_query(sql):
    # conn = connection.get_connection('postgres', 'postgres', '', 'dev.ods.cis.spine2.ncrs.nhs.uk', 5432)
    conn = connection.get_connection('postgres', 'postgres', '', 'localhost', 5432)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute(sql)
    results = cursor.fetchall()
    conn.close()
    return results

def rename_db(old_db_name, new_db_name):
    kill_db_connections(old_db_name)

    rename_db_sql = 'ALTER DATABASE {0} RENAME TO {1};'.format(old_db_name, new_db_name)

    execute_isolated_postgres_statement(rename_db_sql)

def delete_db(target_db_name):

    kill_db_connections(target_db_name)

    delete_sql = 'DROP DATABASE {}'.format(target_db_name)

    execute_isolated_postgres_statement(delete_sql)

# def send_email(sender, recipient, subject, text):
#     password = "kamdevtest1"
#
#     smtp_server = smtplib.SMTP("smtp.gmail.com", 587)
#     smtp_server.ehlo()
#     smtp_server.starttls()
#     smtp_server.login(sender, password)
#     smtp_server.ehlo()
#     message = "Subject: {}\n\n{}".format(subject, text)
#     smtp_server.sendmail(sender, recipient, message)
#     smtp_server.close()


