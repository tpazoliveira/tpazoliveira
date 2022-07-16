import os
import logging
from netmiko import ConnectHandler
from datetime import datetime
import re
from jnpr.junos import Device
from jnpr.junos.exception import ConnectError
from lxml import etree
from jnpr.junos.utils.config import Config


path_file_name = os.path.join("../internal_protect", 'device.log')
logging.basicConfig(level=logging.DEBUG, filename=path_file_name, format=' %(asctime)s - %(message)s')

def get_ssh_pyez_connection(host,hostname,username,password):
    device_connection = Device(host=host, user=username, passwd=password, port='22')
    try:
        device_connection.open()
        device_connection.timeout = 360
        return device_connection
    except ConnectError as error:
        if 'ConnectAuthError' in str(error):
            #set_fail_host_list_file(hostname, host, 'fail_rtpr_apply.csv')
            logging.debug('[get_ssh_pyez_connection]Falha de autenticação, TACACS não habilitado no host ' + str(host) + '. ' + str(error))
            return None
        else:
            #set_fail_host_list_file(hostname, host, 'fail_rtpr_apply.csv')
            logging.debug('[get_ssh_pyez_connection]Não foi possível se conectar ao host ' + str(host) + '. '+ str(error))
            return None

def set_pyez_config(host, hostname, username, password, config_text):
    device_connection = get_ssh_pyez_connection(host,hostname,username, password)
    if device_connection:
        try:
            with Config(device_connection, mode='private') as configuration:
                configuration.load(config_text, format='set')
                if configuration.diff():
                    configuration.commit(timeout=360)
                    logging.debug('[set_pyez_config]Configuração aplicada no host '+ str(hostname))
                else:
                    logging.debug('[set_pyez_config]Configuração já aplicada no host ' + str(hostname))
            device_connection.close()
        except Exception as error:
            if 'RpcError' in str(error) or 'ConfigLoadError' in str(error):
                #set_fail_host_list_file(hostname, host, 'fail_rtpr_apply.csv')
                logging.debug('[set_pyez_config]Não foi possível aplicar a configuração devido ao erro ' + str(error) + ' no host ' + str(hostname))
            else:
                #set_fail_host_list_file(hostname, host, 'fail_rtpr_apply.csv')
                logging.debug('[set_pyez_config]Não foi possível aplicar a configuração devido ao erro ' + str(error) + ' no host ' + str(hostname))
    else:
        logging.debug('[set_pyez_config]Não foi possível estabelecer conexão com o host ' + str(hostname))
        return None

def get_pyez_full_config(host, hostname, username, password):
    device_connection = get_ssh_pyez_connection(host,hostname,username, password)
    if device_connection:
        data = device_connection.rpc.get_config(options={'database' : 'committed'})
        full_configuration = etree.tostring(data, encoding='unicode', pretty_print=True)
        device_connection.close()
        return full_configuration
    else:
        return None

def get_netmiko_connection(host, hostname, username, password, vendor):
    if vendor == 'extreme':
        device = {'device_type': 'extreme', 'host': host, 'username': username, 'password': password, 'port' : 22, 'global_delay_factor': 4, 'banner_timeout': 200, 'conn_timeout':30, 'fast_cli': False} 
        try:
            device_connection = ConnectHandler(**device) 
            device_connection.find_prompt()
            return device_connection
        except:
            device = {'device_type': 'extreme_telnet', 'host': host, 'username': username, 'password': password, 'port' : 23, 'global_delay_factor': 2, 'banner_timeout': 5, 'conn_timeout':5, 'fast_cli': False}
        try:
            device_connection = ConnectHandler(**device)
            device_connection.find_prompt()
            return device_connection
        except Exception as error:
            logging.debug('[get_netmiko_connection]Não foi possível se conectar ao host ' + str(host) + '. Devido ao erro: ' +str(error))
            return None

    if vendor == 'juniper':
        #device = {'device_type': 'juniper_junos', 'host': host, 'username': username, 'password': password, 'port' : 22, 'global_delay_factor': 2, 'banner_timeout': 50, 'conn_timeout':20, 'fast_cli': False} 
        device = {'device_type': 'juniper_junos', 'host': host, 'username': username, 'password': password, 'port' : 22, 'global_delay_factor': 2, 'banner_timeout': 10, 'fast_cli': False}
        try:
            device_connection = ConnectHandler(**device)
            return device_connection
        except Exception as error:
            logging.debug('[get_netmiko_connection]Não foi possível se conectar ao host ' + str(host) + '. Devido ao erro: ' +str(error))
            return None

    if vendor == 'huawei':
        device = {'device_type': 'huawei', 'host': host, 'username': username, 'password': password, 'port' : 22, 'global_delay_factor': 0.1}
        try:
            device_connection = ConnectHandler(**device)
            device_connection.find_prompt()
            return device_connection
        except Exception as error:
            logging.debug('[get_netmiko_connection]Não foi possível se conectar ao host ' + str(host) + '. Devido ao erro: ' +str(error))
            return None        

def set_juniper_netmiko_config(host, hostname, username, password, config_text):    
    device_connection = get_netmiko_connection(host, hostname, username, password, 'juniper')
    if device_connection:
        try:
            device_connection.send_config_set(config_text, delay_factor=40, cmd_verify=False)
            device_connection.commit(confirm=False, check=False)
            device_connection.disconnect()
            status = "ok"
            logging.debug('[set_juniper_netmiko_config]Configuração aplicada no host '+ str(host)+ ' ' +str(hostname))
        except Exception as error:
            logging.debug('[set_juniper_netmiko_config]Não foi possível aplicar a configuração no host ' + str(host) + ' ' + str(hostname)+ ' devido ao erro: ' +str(error))
            status = "configuration_failure"
            return None
    else:
        status = "connection_failure"
        return None

def set_extreme_netmiko_config(host, hostname, username, password, config_text):    
    device_connection = get_netmiko_connection(host, hostname, username, password, 'extreme')
    if device_connection:
        try:
            if config_text:
                for individual_config in config_text:
                    device_connection.send_command(individual_config)
            device_connection.save_config()
            device_connection.disconnect()            
            status = "ok"
            logging.debug('[set_netmiko_config]Configuração aplicada no host '+ str(host)+ ' ' +str(sysname))
        except Exception as error:
            logging.debug('[set_netmiko_config]Não foi possível aplicar a configuração no host ' + str(host) + ' ' + str(sysname)+ ' devido ao erro: ' +str(error))
            status = "configuration_failure"
            return status
    else:
        logging.debug('[set_netmiko_config]Não foi possível aplicar a configuração no host ' + str(host) + ' ' + str(sysname)+ ' devido a falta de conexão')
        status = "connection_failure"
        return status


def get_juniper_netmiko_information(host, hostname, username, password, show_text):
    device_connection = get_netmiko_connection(host, hostname, username, password, 'juniper')
    if device_connection:
        try:
            output = device_connection.send_command_timing(show_text, delay_factor=10, cmd_verify=False)
            device_connection.disconnect()
            return output
        except Exception as error:
            logging.debug('[get_juniper_netmiko_information] Não foi possível obter informação do host ' + str(host) + ' ' + str(hostname)+ ' devido ao erro: ' +str(error))
            return None

def get_extreme_netmiko_information(host, hostname, username, password, show_text):
    device_connection = get_netmiko_connection(host, hostname, username, password,'extreme')
    if device_connection:
        try:
            #output = device_connection.send_command(show_text,cmd_verify=False)
            device_connection.disable_paging(command='disable clipaging', delay_factor=1, cmd_verify=True, pattern=None)
            output = device_connection.send_command(show_text)
            device_connection.disconnect()
            return output
        except Exception as error:
            logging.debug('[get_extreme_information]Não foi possível obter informação do host ' + str(host) + ' ' + str(hostname)+ ' devido ao erro: ' +str(error))
            return None
    else:
        return 'connection_fail'

def get_huawei_netmiko_information(host, sysname, username, password, show_text):
    device_connection = get_netmiko_connection(host, sysname, username, password, 'huawei')
    if device_connection:
        try:
            output = device_connection.send_command(show_text)
            device_connection.disconnect()
            return output
        except Exception as error:
            logging.debug('[get_huawei_netmiko_information]Não foi possível obter informação do host ' + str(host) + ' ' + str(sysname)+ ' devido ao erro: ' +str(error))
            return None



    #TESTAR LIBRARY PyExOS https://github.com/LINXNet/pyexos
    #LIVRO PYENG https://pyneng.readthedocs.io/en/latest/contents.html