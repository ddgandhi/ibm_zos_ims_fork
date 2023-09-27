# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)
from pprint import pprint
import pytest
from tests.functional.module_utils.ims_test_data_definition_utils import ZDDLInputParameters as ip

__metaclass__ = type

# ------------- VARIABLES
ONLINE = ip.ONLINE      # Not Required
OFFLINE = ip.OFFLINE    # Not Required
IMS_ID = ip.IMS_ID          # Not Required  | Required if ONLINE
IRLM_ID = ip.IRLM_ID    # Not Required  | Cannot be specified if ONLINE
RESLIB = ip.RESLIB      # Not Required
PROCLIB = ip.PROCLIB 
STEPLIB = ip.STEPLIB    # Not Required
SQL_INPUT = ip.SQL_INPUT 
SQL_INPUTS = ip.SQL_INPUTS
SQL_FULL_INPUTS = ip.SQL_FULL_INPUTS

# Control statements
VERBOSE = ip.VERBOSE
AUTO_COMMIT = ip.AUTO_COMMIT
SIMULATE = ip.SIMULATE
CREATE_PROGRAM_VIEW = ip.CREATE_PROGRAM_VIEW

# vars for prereqs
COMMAND_INPUT_BUILD = ip.COMMAND_INPUT_BUILD
ACBLIB = ip.ACBLIB
PSBLIB = ip.PSBLIB
DBDLIB = ip.DBDLIB
DBD_NAME = ip.DBD_NAME
DBD_NAMES = ip.DBD_NAMES
# -------------


"""
Work flow for Combination functional tests goes as follows:
1. Send only proclib and sql_input ONLINE IMS ID
2. IMS ID with ONLINE with all variables 
3. IRLM Specified    --------   Not supporting DLI now, comment by now
4. Multi line Sql Input
5. Multi line Sql Input over 6 instructions
6. Offline simulation (DLI test case)
7. Verbose with auto-commit
8. No control statements
9. Simulation, auto-commit and verbose
"""



def validate_data_definition(hosts, online:bool=None, ims_id:str=None,
                            irlm_id:str=None, reslib:list=None, proclib:list=None,
                            steplib:list=None, sql_input:list=None, verbose:bool=None,
                            auto_commit:bool=None, simulate:bool=None, create_program_view:bool=None
                            ):
    arguments = {}
    if online:
        arguments["online"] = online
    if ims_id:
        arguments["ims_id"] = ims_id
    if irlm_id:
        arguments["irlm_id"] = irlm_id
    if reslib:
        arguments["reslib"] = reslib
    if proclib:
        arguments["proclib"] = proclib
    if steplib:
        arguments["steplib"] = steplib
    if sql_input:
        arguments["sql_input"] = sql_input
    if verbose:
        arguments["verbose"] = verbose
    if auto_commit:
        arguments["auto_commit"] = auto_commit
    if simulate:
        arguments["simulate"] = simulate
    if create_program_view:
        arguments["create_program_view"] = create_program_view
    response = hosts.all.ims_ddl(**arguments)
    print("Result:", response)
    for result in response.contacted.values():
        pprint(result)
        print("Message:", result.get('msg'))
        print("Return code:", result.get('rc'))
        assert result.get('msg')
        assert result.get('rc') <= 4


# Check the prereq
def test_managed_acb_prereq(ansible_zos_module):
    hosts = ansible_zos_module
    response = hosts.all.ims_acb_gen(
        command_input=COMMAND_INPUT_BUILD, 
        aclib=ACBLIB, 
        psb_lib=PSBLIB,
        dbd_lib=DBDLIB, 
    )
    for result in response.contacted.values():
        print(result)
        print("Changed:", result['changed'])
        assert result['changed']
        assert result['rc'] == 0


# 1. Send only proclib and sql_input: This is because these are the only two required parameters, it should work without the others(except for IMS_ID when ONLINE)
def test_ims_data_definition_valid_only_proclib_sql_input(ansible_zos_module):
    hosts = ansible_zos_module
    validate_data_definition(hosts, online=None, ims_id=IMS_ID,
                            irlm_id=None, reslib=None, proclib=PROCLIB,
                            steplib=None, sql_input=SQL_INPUTS, verbose=None,
                            auto_commit=None, simulate=None, create_program_view=None)


# 2. IMS ID with ONLINE: Chechs that when given ONLINE and IMS_ID it works
def test_ims_data_definition_valid_ims_id_online(ansible_zos_module):
    hosts = ansible_zos_module
    validate_data_definition(hosts, online=ONLINE, ims_id=IMS_ID,
                            irlm_id=None, reslib=None, proclib=PROCLIB,
                            steplib=None, sql_input=SQL_INPUTS, verbose=None,
                            auto_commit=None, simulate=None, create_program_view=None)
    
# 3. IRLM Specified: Checks that when OFFLINE, works when IRLM_ID is provided (DLI test case)
def test_ims_data_definition_valid_irlm(ansible_zos_module):
    hosts = ansible_zos_module
    validate_data_definition(hosts, online=False, ims_id=None,
                            irlm_id=IRLM_ID, reslib=None, proclib=PROCLIB,
                            steplib=None, sql_input=SQL_INPUTS, verbose=None,
                            auto_commit=None, simulate=None, create_program_view=None)
    
# 4. One line Sql Inputs: Test that it can work with only one sql command
def test_ims_data_definition_valid_multi_sql(ansible_zos_module):
    hosts = ansible_zos_module
    validate_data_definition(hosts, online=None, ims_id=IMS_ID,
                            irlm_id=None, reslib=None, proclib=PROCLIB,
                            steplib=STEPLIB, sql_input=SQL_INPUT, verbose=None,
                            auto_commit=None, simulate=None, create_program_view=None)
    

# 5. Multi line Sql Input over 6 instructions: Test that the DDL module can handle more than six sql commands at once
def test_ims_data_definition_valid_over_six_sql(ansible_zos_module):
    hosts = ansible_zos_module
    validate_data_definition(hosts, online=ONLINE, ims_id=IMS_ID,
                            irlm_id=None, reslib=None, proclib=PROCLIB,
                            steplib=STEPLIB, sql_input=SQL_FULL_INPUTS, verbose=VERBOSE,
                            auto_commit=None, simulate=None, create_program_view=None)

# 6. Offline simulation (DLI test case): Variation of control statements variable for an OFFLINE scenario
def test_ims_data_definition_valid_offline_simulation(ansible_zos_module):
    hosts = ansible_zos_module
    validate_data_definition(hosts, online=OFFLINE, ims_id=None,
                            irlm_id=IRLM_ID, reslib=None, proclib=PROCLIB,
                            steplib=None, sql_input=SQL_INPUT, verbose=None,
                            auto_commit=None, simulate=SIMULATE, create_program_view=None)

# 7. Online verbose with auto-commit: Control statements variation for online and verbose
def test_ims_data_definition_valid_online_verbose_auto_commit(ansible_zos_module):
    hosts = ansible_zos_module
    validate_data_definition(hosts, online=ONLINE, ims_id=IMS_ID,
                            irlm_id=None, reslib=None, proclib=PROCLIB,
                            steplib=None, sql_input=SQL_INPUTS, verbose=VERBOSE,
                            auto_commit=AUTO_COMMIT, simulate=None, create_program_view=None)

# 8. All control statements at once: Test that you can put all the four statemnts as True at once
def test_ims_data_definition_valid_all_control_statements(ansible_zos_module):
    hosts = ansible_zos_module
    validate_data_definition(hosts, online=None, ims_id=None,
                            irlm_id=IRLM_ID, reslib=None, proclib=PROCLIB,
                            steplib=None, sql_input=SQL_INPUTS, verbose=VERBOSE,
                            auto_commit=AUTO_COMMIT, simulate=SIMULATE, create_program_view=CREATE_PROGRAM_VIEW)

# 9. Create Program view with simulation and auto-commit: Variation of the control statements variables
def test_ims_data_definition_valid_control_statements_no_verbose(ansible_zos_module):
    hosts = ansible_zos_module
    validate_data_definition(hosts, online=None, ims_id=None,
                            irlm_id=IRLM_ID, reslib=None, proclib=PROCLIB,
                            steplib=None, sql_input=SQL_INPUTS, verbose=VERBOSE,
                            auto_commit=AUTO_COMMIT, simulate=SIMULATE, create_program_view=None)
