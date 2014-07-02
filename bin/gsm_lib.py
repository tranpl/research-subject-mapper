#/usr/bin/env python

"""
gsm_lib.py

    Stores a collection of utility functions used by
        generate_subject_map.py and generate_subject_map_input.py
"""

__author__      = ""
__copyright__   = "Copyright 2014, University of Florida"
__license__     = "BSD 3-Clause"
__version__     = "0.1"
__email__       = ""
__status__      = "Development"

from lxml import etree
import pprint
import os
import sys
import datetime
import contextlib
import tempfile
import shutil

# This addresses the issues with relative paths
file_dir = os.path.dirname(os.path.realpath(__file__))
goal_dir = os.path.join(file_dir, "../")
proj_root = os.path.abspath(goal_dir)+'/'

sys.path.insert(0, proj_root+'bin/utils/')
from GSMLogger import GSMLogger


'''
Sort element tree based on three given indices.

Keyword argument: data
sorting is based on study_id, form name, then timestamp, ascending order
'''
def sort_element_tree(data):
    # this element holds the subjects that are being sorted
    container = data.getroot()
    container[:] = sorted(container, key=getkey)


'''
Helper function for sorting. Returns keys to sort on.

Keyword argument: elem
returns the corresponding tuple study_id, form_name, timestamp
'''
def getkey(elem):
    research_subject_id = elem.findtext("research_subject_id")
    yob = elem.findtext("yob")
    return (research_subject_id,yob)


'''
Write ElementTree to a file
    takes file_name as input
'''
def write_element_tree_to_file(element_tree, file_name):
    #gsmlogger.logger.debug('Writing ElementTree to %s', file_name)
    element_tree.write(file_name, encoding="us-ascii", xml_declaration=True,method="xml")


'''
Read the config data from settings.ini
'''
def read_config(configuration_directory, filename, settings):
    conf_file = configuration_directory + filename

    # check if the path is valid
    if not os.path.exists(conf_file):
        raise GSMLogger().LogException("Invalid path specified for conf file: " + filename)    

    # test for required parameters
    required_parameters = ['source_data_schema_file', 'site_catalog',
                    'system_log_file']

    for parameter in required_parameters:
        if not settings.hasoption(parameter):
            raise GSMLogger().LogException("read_config: required parameter, "
                + parameter  + "', is not set in " + conf_file)

    # test for required files but only for the parameters that are set
    files = ['source_data_schema_file', 'site_catalog']
    for item in files:
        if settings.hasoption(item):
            if not os.path.exists(configuration_directory + settings.getoption(item)):
                raise LogException("read_config: " + item + " file, '"
                        + settings.getoption(item) + "', specified in "
                        + conf_file + " does not exist")



'''
Helper function for parsing undefined strings
'''
def handle_blanks(s):
    return '' if s is None else s.strip()


'''
Create a folder name with the following format:
    ./out/out_YYYY_mm_dd:00:11:22
'''
def create_temp_dir_debug(existing_folder = './out') :
    prefix = 'out_' + datetime.datetime.now().strftime('%Y_%m_%d-%H_%M_%S')
    mydir = existing_folder + '/' + prefix
    os.mkdir(mydir)
    return mydir

'''
If do_keep_gen_files = True
    create a path like './out/out_YYYY_mm_dd:00:11:22'
else
    create a path using system provided location for a file
'''
def get_temp_path(do_keep_gen_files) :
    if do_keep_gen_files :
        return create_temp_dir_debug('.') + '/'
    else :
        return tempfile.mkdtemp('/')


"""
    Returns a tuple comprising hostname and port number from raw text
    Example:
        From raw: sftp.example.com:1234
        Return  : [sftp.example.com, 1234]
"""
def parse_host_and_port(raw) :
    host_and_port = raw.split(':', 2)
    if (2 == len(host_and_port)) :
        return host_and_port

    info = 'The SFTP uri does not contain a port. Default to port 22'
    print info
    GSMLogger().LogException(info)
    return [raw, 22]

'''
    @return a dictionary representation of a site from xml tree
'''
def get_site_details_as_dict(file_path, site_type):
    valid_site_types = ['data_source', 'data_destination']
    if (not site_type in valid_site_types) :
        raise GSMLogger().LogException("Developer error: Invalid site_type specified") 

    data = {}
    if not os.path.exists(file_path):
        raise GSMLogger().LogException("Error: xml file not found at: " + file_path)

    sites_list = etree.parse(file_path)
    site = sites_list.xpath("(/sites_list/site[@type='" + site_type + "'])[1]")[0]
    data['site_URI']            = handle_blanks( site.findtext('site_URI') )
    data['site_uname']          = handle_blanks( site.findtext('site_uname') )
    data['site_password']       = handle_blanks( site.findtext('site_password') )
    data['site_remotepath']     = handle_blanks( site.findtext('site_remotepath') )
    data['site_contact_email']  = handle_blanks( site.findtext('site_contact_email') )
    data['site_key_path']       = handle_blanks( site.findtext('site_key_path') )

    return data

