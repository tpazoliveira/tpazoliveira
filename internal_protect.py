import sys
import logging
import os
import csv
from datetime import datetime
import re
from netaddr import IPNetwork, IPAddress
from lxml import etree
import pandas as pd
from modules import device
from modules import tools
from modules.data import Data


path_file_name = os.path.join("../internal_protect", 'internal_protect.log')
logging.basicConfig(level=logging.DEBUG, filename=path_file_name, format=' %(asctime)s - %(message)s')


def get_list_from_file(filename):
    ip_list = []
    hostname_list = []
    host_list = []
    try:
        path_file_name = os.path.join("../internal_protect/utils", filename)
        with open(path_file_name) as csv_file:
            if filename == 'full_prefix_list_checked.csv':
                csv_reader = csv.reader(csv_file)
                for ip in csv_reader:
                    ip_list.append(ip[0])
                return ip_list                
            elif filename.startswith('fail'):
                csv_reader = csv.reader(csv_file, delimiter = ' ')
                for hostname, host in csv_reader:
                    hostname_list.append(hostname)
                    #host_list.append(host)
                return hostname_list                
            else:
                csv_reader = csv.reader(csv_file, delimiter = ' ')
                for ip, hostname, host in csv_reader:
                    ip_list.append(ip)
                    hostname_list.append(hostname)
                    host_list.append(host)
                return ip_list, hostname_list, host_list
    except Exception as error:
        if str(error).startswith('[Errno 2] No such file or directory'):
            if filename.startswith('fail'):
                return None
            else:
                return None, None, None
        else:
            logging.debug('[get_ip_list_from_file]Não foi possível carregar os hosts. Erro: ' + str(error))
            return None, None, None

def set_prefix_list_file(ip, hostname, host, filename):
    if not filename:
        filename = hostname
    try:
        path_file_name = os.path.join("../internal_protect/utils", filename)
        write_file = open(path_file_name, "a")
        if not hostname and not host:
            writer = csv.writer(write_file)
            writer.writerow([ip])
            write_file.close()
        else:
            writer = csv.writer(write_file, delimiter = ' ')
            writer.writerow([ip, hostname, host])
            write_file.close()
    except Exception as error:
        logging.debug('[set_prefix_list_file]Não foi possível inserir os host '+ str(host)+' '+ str(hostname)+' no arquivo. Erro: ' +str(error))

def set_fail_host_list_file(hostname, host, filename):
    try:
        path_file_name = os.path.join("../internal_protect/utils", filename)
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
    extreme_hostname_list = db_object.get_data_all("select hostname_equipamento from inventario where fabricante = 'Extreme' AND tipo_acesso in('ssh', 'telnet') AND status LIKE '%ok%'")
    extreme_host_list = db_object.get_data_all("select ip from inventario where fabricante = 'Extreme' AND tipo_acesso in('ssh', 'telnet') AND status LIKE '%ok%'")
    huawei_hostname_list = db_object.get_data_all("select hostname_equipamento from inventario where fabricante = 'Huawei' AND tipo_acesso in('ssh', 'telnet') AND status LIKE '%ok%'")
    huawei_host_list = db_object.get_data_all("select ip from inventario where fabricante = 'Huawei' AND tipo_acesso in('ssh', 'telnet') AND status LIKE '%ok%'")    
    public_network_list = ['177.101.192.0/19','187.84.192.0/19','200.49.32.0/19','170.78.76.0/22','177.101.224.0/19','187.33.32.0/20','200.152.240.0/20','189.201.200.0/21','177.220.192.0/19','189.45.32.0/19','167.249.152.0/22','167.249.232.0/22','177.220.224.0/19','189.126.192.0/20','168.205.156.0/22', '186.249.0.0/20', '187.1.80.0/20', '179.107.96.0/20', '177.107.128.0/20', '177.107.144.0/20']
    #############################################################################################################################

    #############################################################################################################################
    ## OBTEM TODOS OS IPs VÁLIDOS DOS SWITCHS E ROTEADORES HUAWEI ##
    tools.delete_file('fail_get_ip_list.csv')
    for count, host in enumerate(huawei_host_list):
        ip_list = []
        huawei_ne_command_result = device.get_huawei_netmiko_information(host, huawei_hostname_list[count], username, password, 'display ip interface brief | include up')
        if huawei_ne_command_result:
            if huawei_ne_command_result == 'connection_fail':
                set_fail_host_list_file(huawei_hostname_list[count], host, 'fail_get_ip_list.csv')
                logging.debug('Não foi possível se conectar ao host ' + str(huawei_hostname_list[count]) )                
            else:
                huawei_ne_command_result = huawei_ne_command_result.split()
                for row in huawei_ne_command_result:
                    if re.search('^[0-9][0-9]?[0-9]?.[0-9][0-9]?[0-9]?.[0-9][0-9]?[0-9]?.[0-9][0-9]?[0-9]?/[0-9][0-9]$', row):
                        ip_list.append(row[:-3])
                tools.delete_file(huawei_hostname_list[count])
                if ip_list:
                    for ip in ip_list:
                        set_prefix_list_file(ip, huawei_hostname_list[count], host, None)
                    logging.debug('Passo 1 - Criação dos aquivos de prefixos (concluído).') 
                else:
                    logging.debug('Não existe IP válido configurado no host ' + str(huawei_hostname_list[count]))
                    tools.delete_file(huawei_hostname_list[count])
        else:
            logging.debug('Não existe IP válido configurado no host ' + str(huawei_hostname_list[count]))
            tools.delete_file(huawei_hostname_list[count])
    #print('Processo concluído')
    #exit()
    #############################################################################################################################
    ## OBTEM TODOS OS IPs VÁLIDOS DOS SWITCHS EXTREME ##
    tools.delete_file('fail_get_ip_list.csv')
    for count, host in enumerate(extreme_host_list):
        ip_list = []
        command_result = device.get_extreme_netmiko_information(host, extreme_hostname_list[count], username, password, 'show iproute origin direct vr IP-CORP | include "#d   "')   
        if command_result:
            if command_result == 'connection_fail':
                set_fail_host_list_file(extreme_hostname_list[count], host, 'fail_get_ip_list.csv')
                logging.debug('Não foi possível se conectar ao host ' + str(extreme_hostname_list[count]) )                
            else:
                command_result = command_result.split()
                for row in command_result:
                    if re.search('^[0-9][0-9]?[0-9]?.[0-9][0-9]?[0-9]?.[0-9][0-9]?[0-9]?.[0-9][0-9]?[0-9]?$', row):
                        ip_list.append(row)
                tools.delete_file(extreme_hostname_list[count])
                if ip_list:
                    for ip in ip_list:
                        set_prefix_list_file(ip, extreme_hostname_list[count], host, None)
                    logging.debug('Passo 1 - Criação dos aquivos de prefixos (concluído).') 
                else:
                    logging.debug('Não existe IP válido configurado no host ' + str(extreme_hostname_list[count]))
                    tools.delete_file(extreme_hostname_list[count])
        else:
            logging.debug('Não existe IP válido configurado no host ' + str(extreme_hostname_list[count]))
            tools.delete_file(extreme_hostname_list[count])
    #print('Processo concluído')
    #exit()
    #############################################################################################################################
    ## SALVA TODOS OS IPs VÁLIDOS OBTIDOS DOS SWITCHS EXTREME EM UM ARQUIVO ## 
    zte_hostname_list = ['gpon-01-rs-pae-stc']
    full_hostname_list = extreme_hostname_list + huawei_hostname_list + zte_hostname_list
    tools.delete_file('full_prefix_list.csv')

    for hostname in full_hostname_list:
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
    logging.debug('Passo 2 - Criação do arquivo full_prefix_list_checked.csv (concluído).')
    #print('Processo concluído')
    #exit()
    #############################################################################################################################
    ## APLICA AS CONFIGURAÇÕES NOS RTPRs ##
    tools.delete_file('fail_rtpr_apply.csv')
    #rtpr_host_list = ['10.255.211.0', '10.255.214.0', '172.28.0.180', '172.28.24.23', '10.255.255.248', '10.255.253.1', '10.254.255.1', '187.1.95.192', '187.1.95.194']
    rtpr_host_list = ['10.255.211.0', '10.255.214.0', '172.28.0.180', '172.28.24.23', '10.255.255.248', '10.255.253.1', '10.254.255.1', '187.1.95.192']
    rtpr_hostname_list = ['RTPR-01-SP-SPO-BRF', 'RTPR-01-SP-SPO-VRO', 'RTPR-01-RJ-RJO-SCR-RE0', 'RTPR-01-RJ-RJO-TLP-RE0', 'cgborder-rs-pae-01', 'rtpr-01-pr-cta-vqm', 'xgborder-sc-pac-01','SPO-VRO-01-RE-PE-M104-200', 'RT-COR-MX80-STE-01']
    #rtpr_host_list = ['187.1.95.194']
    #rtpr_hostname_list = ['RT-COR-MX80-STE-01']
    config_text = 'delete policy-options prefix-list internal_protocol_local\n edit policy-options prefix-list internal_protocol_local '
    ip_list = get_list_from_file('full_prefix_list_checked.csv')
    for ip in ip_list:
        config_text = config_text + '\n' + 'set ' + str(ip)
    for count, rtpr in enumerate(rtpr_host_list):
        if rtpr.startswith('187.'):
            username = 'vV0ge1_CgR'
            password = '#V0ge!-@Te1ec0m_'
            '''if rtpr == '187.1.95.194':
                public_network_advertised = []
                local_ip_list = []
                show_command_result = device.get_juniper_netmiko_information('187.1.95.194', 'RT-COR-MX80-STE-01', username, password, 'show route advertising-protocol bgp 187.1.89.208 | no-more')
                #show_command_result = get_juniper_netmiko_information('187.1.95.194', 'RT-COR-MX80-STE-01', username, password, 'show route advertising-protocol bgp 187.1.89.208 | no-more')
                if show_command_result:
                    show_command_result = show_command_result.split()
                    for row in show_command_result:
                        if re.search('^[0-9][0-9]?[0-9]?.[0-9][0-9]?[0-9]?.[0-9][0-9]?[0-9]?.[0-9][0-9]?[0-9]?/[0-9][0-9]$', row):
                                public_network_advertised.append(row)
                    config_text = 'delete policy-options prefix-list internal_protocol_local\n edit policy-options prefix-list internal_protocol_local '
                    for ip in ip_list:
                        for network in public_network_advertised:
                            ip_aux = ip.replace('/32', '')
                            if IPAddress(ip_aux) in IPNetwork(network):    
                                config_text = config_text + '\n' + 'set ' + str(ip)
                                local_ip_list.append(ip)
                    if local_ip_list:
                        device.set_juniper_netmiko_config(rtpr, rtpr_hostname_list[count], username, password, config_text)
                        #set_juniper_netmiko_config(rtpr, rtpr_hostname_list[count], username, password, config_text)
                    else:
                        logging.debug('Nenhuma configuração aplicada no host ' + str(rtpr_hostname_list[count]) + '. Os IPs não pertencem a prefixos anunciadas ao PNI Google-MG.')
                else:
                    set_fail_host_list_file(rtpr_host_list[count], rtpr, 'fail_rtpr_apply.csv')             
            else:
                device.set_pyez_config(rtpr, rtpr_hostname_list[count],username, password, config_text)'''
            device.set_pyez_config(rtpr, rtpr_hostname_list[count],username, password, config_text)
        else:
            device.set_pyez_config(rtpr, rtpr_hostname_list[count],username, password, config_text)
    logging.debug('Passo 3 - Aplicacação das configurações nos RTPRs (concluído).')
    #print('Processo concluído')
    #exit()
    #############################################################################################################################
    ## REALIZA NOTIFICAÇÃO VIA EMAIL EM CASO DE FALHA ##
    hostname_failure_list = get_list_from_file('fail_get_ip_list.csv')
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
        tools.set_email(email_subject, email_content)
        logging.debug('Passo 4 - Notificação em caso de falha (concluído).')
        logging.debug('Processo concluído')
        exit()
    elif hostname_failure_list:
        email_subject = '[Notificação de falha] Bloqueio externo SW Extreme'
        email_content = 'Não foi possível se conectar aos seguintes switchs:'
        for hostname in hostname_failure_list:
            email_content = email_content + '\n' + str(hostname)
        email_content = str(email_content) + '\n\n'
        tools.set_email(email_subject, email_content)
        logging.debug('Passo 4 - Notificação em caso de falha (concluído).')
        logging.debug('Processo concluído')
        exit()
    elif rtpr_failure_list:
        email_subject = '[Notificação de falha] Bloqueio externo SW Extreme'
        email_content = 'Não foi possível aplicar as configurações nos seguintes RTPRs:'
        for rtpr in rtpr_failure_list:
            email_content = email_content + '\n' + str(rtpr)
        email_content = str(email_content) + '\n\n'
        tools.set_email(email_subject, email_content)
        logging.debug('Passo 4 - Notificação em caso de falha (concluído).')
        logging.debug('Processo concluído')
        exit()
    else:
        logging.debug('Passo 4 - Notificação em caso de falha (concluído).')
        logging.debug('Processo concluído')
        exit()

    # TESTAR LIBRARY PyExOS https://github.com/LINXNet/pyexos
    # LIVRO PYENG https://pyneng.readthedocs.io/en/latest/contents.html
    # EXEMPLOS PY-ZABBIX: https://github.com/fabianlee/blogcode/tree/master/py-zabbix
    # EXEMPLOS PY-ZABBIX:https://fabianlee.org/2017/04/21/zabbix-accessing-zabbix-using-the-py-zabbix-python-module/