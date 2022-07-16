# -*- coding: utf-8 -*-

import pymysql

class Data():

  def set_data(self,sql_statement):
    try:
      db_connection = pymysql.connect(user='vogel',password='vogel@123',host='10.0.52.47',database='inventario_vogel',use_unicode=True,charset='utf8')
      db_cursor = db_connection.cursor()
      db_cursor.execute(sql_statement)
      db_connection.commit()
      db_connection.close()
      return 1
    except pymysql.err.OperationalError as err:
      print("Acesso ao banco de dados negado. Causa: "+str(err))


  def get_data_all(self,sql_statement):
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


  def get_data_one(self,sql_statement):
    try:
      db_connection = pymysql.connect(user='vogel',password='vogel@123',host='10.0.52.47',database='inventario_vogel',use_unicode=True,charset='utf8')
      db_cursor = db_connection.cursor()
      db_cursor.execute(sql_statement)
      result = db_cursor.fetchone()
      db_connection.close()
      return result
    except pymysql.err.OperationalError as err:
      print("Acesso ao banco de dados negado. Causa: "+str(err))

  def delete_data(self,sql_statement):
    try:
      db_connection = pymysql.connect(user='vogel',password='vogel@123',host='10.0.52.47',database='inventario_vogel',use_unicode=True,charset='utf8')
      db_cursor = db_connection.cursor()
      db_cursor.execute(sql_statement)
      db_connection.commit()
      db_connection.close()
      return 1
    except pymysql.err.OperationalError as err:
      print("Acesso ao banco de dados negado. Causa: "+str(err))
