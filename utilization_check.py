import sys
import logging
import os
import csv
from datetime import datetime
import re
from netaddr import IPNetwork, IPAddress
import pandas as pd
from modules import device
from modules import tools
from modules.data import Data
#from data import Data 


path_file_name = os.path.join("../internal_protect", 'utilization_check.log')
logging.basicConfig(level=logging.DEBUG, filename=path_file_name, format=' %(asctime)s - %(message)s')


def get_list_from_file(filename):
    hostname_list = []
    host_list = []
    configured_l2vpn_list = []
    active_l2vpn_list = []
    try:
        path_file_name = os.path.join("../internal_protect/utils", filename)
        with open(path_file_name) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter = ' ')
            for host, hostname, configured_l2vpn, active_l2vpn in csv_reader:
                hostname_list.append(hostname)
                configured_l2vpn_list.append(configured_l2vpn)
                active_l2vpn_list.append(active_l2vpn)
            return hostname_list, configured_l2vpn_list, active_l2vpn_list
    except Exception as error:
        if str(error).startswith('[Errno 2] No such file or directory'):
            if filename.startswith('fail'):
                return None
            else:
                return None, None, None
        else:
            logging.debug('[get_list_from_file]Não foi possível carregar os hosts. Erro: ' + str(error))
            return None, None, None

def set_utilization_information_file(ip, hostname, configured_l2vpn, active_l2vpn, percentage, filename):
    print(ip, hostname, configured_l2vpn, active_l2vpn, percentage, filename)
    try:
        path_file_name = os.path.join("../internal_protect/utils", filename)
        if os.path.exists(path_file_name):
            write_file = open(path_file_name, "a")
            writer = csv.writer(write_file, delimiter = ' ')
            writer.writerow([ip, hostname, configured_l2vpn, active_l2vpn, percentage])
        else:
            write_file = open(path_file_name, "a")
            writer = csv.writer(write_file, delimiter = ' ')
            writer.writerow(['IP', 'HOST', 'VPLS_CONFIGURADO', 'VPLS_ATIVO', 'VPLS_INATIVO'])
        write_file.close()
    except Exception as error:
        logging.debug('[set_prefix_list_file]Não foi possível inserir os host '+ str(host)+' '+ str(hostname)+' no arquivo. Erro: ' +str(error))

def set_information_to_file(ip, hostname,info, filename):
    try:
        path_file_name = os.path.join("../internal_protect/utils", filename)
        write_file = open(path_file_name, "a")
        writer = csv.writer(write_file)
        writer = csv.writer(write_file, delimiter = ' ')
        writer.writerow([hostname, host, info])
        write_file.close()
    except Exception as error:
        logging.debug('[set_prefix_list_file]Não foi possível inserir os host '+ str(host)+' '+ str(hostname)+' no arquivo. Erro: ' +str(error))

def set_fail_host_list_file(hostname, host, filename):
    try:
        #path_file_name = os.path.join("../internal_protect/utils", filename)
        write_file = open(path_file_name, "a")
        writer = csv.writer(write_file)
        writer = csv.writer(write_file, delimiter = ' ')
        writer.writerow([hostname, host])
        write_file.close()
    except Exception as error:
        logging.debug('[set_fail_host_list_file]Não foi possível inserir os host '+ str(host)+' '+ str(hostname)+' no arquivo. Erro: ' +str(error))



if __name__ == '__main__':

    username = 'oxidized'
    password = '0x1d1zed_v0ge!'


    #############################################################################################################################
    ## OBTEM TODOS OS IPs E HOSTNAMEs DO BANCO DE DADOS ##
    db_object = Data()
    hostname_list = db_object.get_data_all("select hostname_equipamento from inventario where fabricante like '%Extreme%' AND status LIKE '%ok%'")
    host_list = db_object.get_data_all("select ip from inventario where fabricante like '%Extreme%' AND status LIKE '%ok%'")
    #############################################################################################################################
 
    ############################################################################################################################
    ## OBTEM A LISTA DE TODOS OS LDP PEERS ##
    for host_count, host in enumerate(host_list):
        ldp_peer_list = []
        command_result = device.get_extreme_netmiko_information(host, hostname_list[host_count], username, password, 'show mpls ldp peer | include Operational')   
        if command_result:
            if command_result == 'connection_fail':
                logging.debug('Não foi possível se conectar ao host ' + str(hostname_list[host_count]))
                set_information_to_file(host, hostname_list[host_count], 'failure','Extreme_ldp_peer_information.csv')                
            else:
                command_result = command_result.split()
                for result_count, row in enumerate(command_result):
                    if re.search(':0$', row):
                        ldp_peer_list.append(row.replace(':0', ''))
                set_information_to_file(host, hostname_list[host_count], len(ldp_peer_list),'Extreme_ldp_peer_information.csv')
                logging.debug('Obtido informação do host ' + str(hostname_list[host_count]) + ' com sucesso.')
        else:
            set_information_to_file(host, hostname_list[host_count], 'no_result','Extreme_ldp_peer_information.csv')
    #print('Processo concluído')
    #exit()
    #############################################################################################################################

    ## CHECA OS SWITCHS QUE POSSUEM MAIS DE 50 VPLSs INACTIVE
    '''hostname_list, configured_l2vpn_list, active_l2vpn_list = get_list_from_file('Extreme_utilization_information.csv')
    for count, configured_l2vpn in enumerate(configured_l2vpn_list):
        if (int(configured_l2vpn) - int(active_l2vpn_list[count])) >= 50:
            print(hostname_list[count], 'VPLS configurados: ' + str(configured_l2vpn), 'VPLS down: ' +str(int(configured_l2vpn) - int(active_l2vpn_list[count])))
    exit()'''
    ############################################################################################################################

    ## OBTEM A QUANTIDADE DE VPLS CONFIGURADOS NO SWITCH ##
    #tools.delete_file('Extreme_utilization_information.csv')
    for host_count, host in enumerate(host_list):
        command_result = device.get_extreme_netmiko_information(host, hostname_list[host_count], username, password, 'show vpls summary | include L2VPNs')   
        if command_result:
            if command_result == 'connection_fail':
                logging.debug('Não foi possível se conectar ao host ' + str(hostname_list[host_count]))
                set_utilization_information_file(host, hostname_list[host_count], 'failure', 'failure', 'failure', 'Extreme_utilization_information.csv')                
            else:
                command_result = command_result.split()
                for result_count, row in enumerate(command_result):
                    percentage = '100%'
                    if re.search('^[0-9][0-9]?[0-9]?[0-9]?$', row):
                        if result_count == 5:
                            configured_l2vpn = int(row)
                        if result_count == 11:
                            active_l2vpn = int(row)
                            if active_l2vpn != 0:
                                percentage = round((active_l2vpn - configured_l2vpn) / configured_l2vpn * 100)
                                percentage = str(abs(percentage)) + '%'
                            if configured_l2vpn == active_l2vpn:
                                set_utilization_information_file(host, hostname_list[host_count], configured_l2vpn, active_l2vpn, percentage, 'Extreme_utilization_information.csv')
                            else:
                                set_utilization_information_file(host, hostname_list[host_count], configured_l2vpn, active_l2vpn, percentage, 'Extreme_utilization_information.csv')
                            #print(host, hostname_list[host_count], configured_l2vpn, active_l2vpn, percentage)
                            logging.debug('Obtido informação do host ' + str(hostname_list[host_count]) + ' com sucesso.')
        else:
            set_utilization_information_file(host, hostname_list[host_count], 'no_result', 'no_result', 'no_result', 'Extreme_utilization_information.csv')
            #logging.debug('Não existe VPLS configurado no host ' + str(hostname_list[host_count]))
    
    print('Processo concluído')
    exit()
    #############################################################################################################################
    ## SALVA TODOS OS IPs VÁLIDOS OBTIDOS DOS SWITCHS EXTREME EM UM ARQUIVO ## 
    #tools.delete_file('full_prefix_list.csv')
    for hostname in hostname_list:
        ip_list, hostname_list, host_list = get_list_from_file(hostname)
        if ip_list:
            for count, ip in enumerate(ip_list):
                for network in public_network_list:
                    if IPAddress(ip) in IPNetwork(network):    
                        set_prefix_list_file(str(ip)+'/32', None, None, 'full_prefix_list.csv')
                        #set_prefix_list_file(str(ip)+'/32', hostname, host_list[count], 'full_prefix_list.csv')
    # Remove Duplicate
    original_file = os.path.join("../internal_protect/utils", 'full_prefix_list.csv')
    df = pd.read_csv(original_file)
    df.drop_duplicates(subset=None, inplace=True)
    # Write the results to a different file
    result_file = os.path.join("../internal_protect/utils", 'full_prefix_list_checked.csv')
    file_name_output = result_file
    df.to_csv(file_name_output, index=False)
    #print('Processo concluído')
    #exit()
    #############################################################################################################################
    ## REALIZA NOTIFICAÇÃO VIA EMAIL EM CASO DE FALHA ##
    '''hostname_failure_list = get_list_from_file('')
    rtpr_failure_list = get_list_from_file('fail_rtpr_apply.csv')
    if hostname_failure_list and rtpr_failure_list:
        email_subject = '[Notificação de falha] Bloqueio externo SW Extreme'
        email_content = 'Não foi possível se conectar aos seguintes switchs:'
        for hostname in hostname_failure_list:
            email_content = email_content + '\n' + str(hostname)
        email_content = str(email_content) + '\n\n'
        email_content = email_content + 'Não foi possível aplicar as configurações nos seguintes RTPRs:'
        for rtpr in rtpr_failure_list:
            email_content = email_content + '\n' + str(rtpr)
        email_content = str(email_content) + '\n\n'
        set_email(email_subject, email_content)
        logging.debug('Processo concluído')
        #print('Processo concluído')
        exit()
    elif hostname_failure_list:
        email_subject = '[Notificação de falha] Bloqueio externo SW Extreme'
        email_content = 'Não foi possível se conectar aos seguintes switchs:'
        for hostname in hostname_failure_list:
            email_content = email_content + '\n' + str(hostname)
        email_content = str(email_content) + '\n\n'
        set_email(email_subject, email_content)
        logging.debug('Processo concluído')
        #print('Processo concluído')
        exit()
    elif rtpr_failure_list:
        email_subject = '[Notificação de falha] Bloqueio externo SW Extreme'
        email_content = 'Não foi possível aplicar as configurações nos seguintes RTPRs:'
        for rtpr in rtpr_failure_list:
            email_content = email_content + '\n' + str(rtpr)
        email_content = str(email_content) + '\n\n'
        set_email(email_subject, email_content)
    else:
        logging.debug('Processo concluído')
        #print('Processo concluído')
        exit()'''

    # TESTAR LIBRARY PyExOS https://github.com/LINXNet/pyexos
    # LIVRO PYENG https://pyneng.readthedocs.io/en/latest/contents.html
    # EXEMPLOS PY-ZABBIX: https://github.com/fabianlee/blogcode/tree/master/py-zabbix
    # EXEMPLOS PY-ZABBIX:https://fabianlee.org/2017/04/21/zabbix-accessing-zabbix-using-the-py-zabbix-python-module/