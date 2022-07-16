# -*- coding: utf-8 -*-
import sys
import logging
import os
import csv
from netaddr import IPNetwork, IPAddress
import pymysql

def get_data_all(sql_statement):
    result = []
    try:
        db_connection = pymysql.connect(user='vogel',password='vogel@123',host='10.0.52.47',database='inventario_vogel',use_unicode=True,charset='utf8')      
        db_cursor = db_connection.cursor()
        db_cursor.execute(sql_statement)
        aux_result = db_cursor.fetchall()
        db_connection.close()
        for row in aux_result:
            result.append(row[0])
        return result
    except pymysql.err.OperationalError as err:
        print("Acesso ao banco de dados negado. Causa: "+str(err))


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


if __name__ == '__main__':

    username = 'oxidized'
    password = '0x1d1zed_v0ge!'


    #############################################################################################################################
    ## OBTEM TODOS OS IPs E HOSTNAMEs DO BANCO DE DADOS ##
    #db_object = Data()
    extreme_hostname_list = get_data_all("select hostname_equipamento from inventario where fabricante = 'Extreme' AND tipo_acesso in('ssh', 'telnet') AND status LIKE '%ok%'")
    extreme_host_list = get_data_all("select ip from inventario where fabricante = 'Extreme' AND tipo_acesso in('ssh', 'telnet') AND status LIKE '%ok%'")
    huawei_hostname_list = get_data_all("select hostname_equipamento from inventario where fabricante = 'Huawei' AND tipo_acesso in('ssh', 'telnet') AND status LIKE '%ok%'")
    huawei_host_list = get_data_all("select ip from inventario where fabricante = 'Huawei' AND tipo_acesso in('ssh', 'telnet') AND status LIKE '%ok%'")    
    public_network_list = ['177.101.192.0/19','187.84.192.0/19','200.49.32.0/19','170.78.76.0/22','177.101.224.0/19','187.33.32.0/20','200.152.240.0/20','189.201.200.0/21','177.220.192.0/19','189.45.32.0/19','167.249.152.0/22','167.249.232.0/22','177.220.224.0/19','189.126.192.0/20','168.205.156.0/22', '186.249.0.0/20', '187.1.80.0/20', '179.107.96.0/20', '177.107.128.0/20', '177.107.144.0/20']
    #############################################################################################################################

    #############################################################################################################################
    ## SALVA TODOS OS IPs VÁLIDOS OBTIDOS DOS SWITCHS EXTREME EM UM ARQUIVO ## 
    zte_hostname_list = ['gpon-01-rs-pae-stc']
    full_hostname_list = extreme_hostname_list + huawei_hostname_list + zte_hostname_list

    for hostname in full_hostname_list:
        ip_list, hostname_list, host_list = get_list_from_file(hostname)
        if ip_list:
            for count, ip in enumerate(ip_list):
                for network in public_network_list:
                    if IPAddress(ip) in IPNetwork(network):    
                        print(ip, hostname_list[count], host_list[count])
    exit()
    #############################################################################################################################