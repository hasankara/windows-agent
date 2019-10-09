#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>

import datetime
import json
import uuid
from uuid import getnode as get_mac
from base.scope import Scope
from base.messaging.anonymous_messenger import AnonymousMessenger
from base.system.system import System
from base.util.util import Util
from base.timer.setup_timer import SetupTimer
from base.timer.timer import Timer
import re
import os

class Registration:
    def __init__(self):
        scope = Scope().get_instance()
        self.logger = scope.get_logger()
        self.message_manager = scope.get_message_manager()
        self.event_manager = scope.get_event_manager()
        self.messenger = scope.get_messenger()
        self.conf_manager = scope.get_configuration_manager()
        self.db_service = scope.get_db_service()
        self.util = Util()
        self.servicename='im.liderahenk.org'

        #self.event_manager.register_event('REGISTRATION_RESPONSE', self.registration_process)
        self.event_manager.register_event('REGISTRATION_SUCCESS', self.registration_success)
        self.event_manager.register_event('REGISTRATION_ERROR', self.registration_error)


        if self.is_registered():
            self.logger.debug('Ahenk already registered')
        else:
            self.register(True)

    def registration_request(self, hostname,username,password):

        self.logger.debug('Requesting registration')
        # SetupTimer.start(Timer(System.Ahenk.registration_timeout(), timeout_function=self.registration_timeout,checker_func=self.is_registered, kwargs=None))

        self.servicename = self.conf_manager.get("CONNECTION", "servicename")

        self.host = hostname
        self.user_name = username
        self.user_password = password

        if(username is None and password is None and self.host is None):

            self.host = self.conf_manager.get("CONNECTION", "host")

            user_name = os.getlogin()
            self.logger.debug('User : '+ str(user_name))
            # pout = Util.show_registration_message(user_name,'Makineyi Lider MYS sistemine kaydetmek için bilgileri ilgili alanlara giriniz. LÜTFEN DEVAM EDEN İŞLEMLERİ SONLANDIRDIĞINZA EMİN OLUNUZ !',
            #                                       'LIDER MYS SISTEMINE KAYIT', self.host)
            # self.logger.debug('pout : ' + str(pout))
            # field_values = pout.split(' ')
            # user_registration_info = list(field_values)

            if self.host == '':
                self.host = "192.168.56.145"
                self.user_name = "test_ldap_user"
                self.user_password = "secret"
            else:
                # self.user_name = user_registration_info[0]
                # self.user_password = user_registration_info[1]
                self.user_name = "test_ldap_user"
                self.user_password = "secret"

        #anon_messenger = AnonymousMessenger(self.message_manager.registration_msg(user_name,user_password), self.host,self.servicename)
        #anon_messenger.connect_to_server()

        self.logger.debug('Requesting registration')
        SetupTimer.start(Timer(System.Ahenk.registration_timeout(), timeout_function= self.registration_timeout, checker_func = self.is_registered, kwargs=None))
        anon_messenger = AnonymousMessenger(self.message_manager.registration_msg(self.user_name, self.user_password), self.host, self.servicename)
        anon_messenger.connect_to_server()

    def ldap_registration_request(self):
        self.logger.info('Requesting LDAP registration')
        self.messenger.send_Direct_message(self.message_manager.ldap_registration_msg())

    def registration_success(self, reg_reply):
        self.logger.info('Registration update starting')
        try:
            dn = str(reg_reply['agentDn'])
            self.logger.info('Current dn:' + dn)
            self.logger.info('updating host name and service')
            self.update_registration_attrs(dn)
            self.install_and_config_ldap(reg_reply)

        except Exception as e:
            self.logger.error('Registration error. Error Message: {0}.'.format(str(e)))
            print(e)
            raise

    def update_registration_attrs(self, dn=None):
        self.logger.debug('Registration configuration is updating...')
        self.db_service.update('registration', ['dn', 'registered'], [dn, 1], ' registered = 0')

        if self.conf_manager.has_section('CONNECTION'):
            self.conf_manager.set('CONNECTION', 'uid',
                                  self.db_service.select_one_result('registration', 'jid', ' registered=1'))
            self.conf_manager.set('CONNECTION', 'password',
                                  self.db_service.select_one_result('registration', 'password', ' registered=1'))

            if  self.host and self.servicename:
                self.conf_manager.set('CONNECTION', 'host', self.host)
                self.conf_manager.set('CONNECTION', 'servicename', self.servicename)

            # TODO  get file path?
            with open('C:\\Users\\hasan\\ahenk\\ahenk.conf', 'w') as configfile:
                self.conf_manager.write(configfile)
            self.logger.debug('Registration configuration file is updated')

    def install_and_config_ldap(self, reg_reply):
        self.logger.info('ldap install process starting')
        # server_address = str(reg_reply['ldapServer'])
        # dn = str(reg_reply['ldapBaseDn'])
        # version = str(reg_reply['ldapVersion'])
        # admin_dn = str(reg_reply['ldapUserDn']) # get user full dn from server.. password same
        #admin_password = self.user_password # same user get from server
        # admin_password = self.db_service.select_one_result('registration', 'password', ' registered=1')
        # if server_address != '' and dn != '' and  version != '' and admin_dn != '' and admin_password != '':
        #     self.logger.info("SSSD configuration process starting....")
        #     #self.ldap_login.authenticate(server_address, dn, admin_dn, admin_password)
        #     self.logger.info("SSSD configuration process starting....")
        # else :
        #     raise Exception(
        #         'LDAP Ayarları yapılırken hata oluştu. Lütfen ağ bağlantınızı kontrol ediniz. Deponuzun güncel olduğundan emin olunuz.')

    def registration_error(self, reg_reply):
       self.re_register()

    def is_registered(self):
        try:
            if str(System.Ahenk.uid()):
                return True
            else:
                return False
        except:
            return False

    def is_ldap_registered(self):
        dn = self.db_service.select_one_result('registration', 'dn', 'registered = 1')
        if dn is not None and dn != '':
            return True
        else:
            return False

    def register(self, uuid_depend_mac=False):
        cols = ['jid', 'password', 'registered', 'params', 'timestamp']
        # vals = [str(System.Os.hostname()), str(self.generate_uuid(uuid_depend_mac)), 0,
        #         str(self.get_registration_params()), str(datetime.datetime.now().strftime("%d-%m-%Y %I:%M"))]

        vals = [str(System.Os.hostname()), str(self.generate_uuid(uuid_depend_mac)), 0,
                str("{\"test_param\":\"param_value\"}"), str(datetime.datetime.now().strftime("%d-%m-%Y %I:%M"))]

        self.db_service.delete('registration', ' 1==1 ')
        self.db_service.update('registration', cols, vals)
        self.logger.debug('Registration parameters were created')

    def get_registration_params(self):
        parts = []
        for part in System.Hardware.Disk.partitions():
            parts.append(part[0])

        params = {
            'ipAddresses': str(System.Hardware.Network.ip_addresses()).replace('[', '').replace(']', ''),
            'macAddresses': str(System.Hardware.Network.mac_addresses()).replace('[', '').replace(']', ''),
            'hostname': System.Os.hostname(),
            'os.name': System.Os.name(),
            'os.version': System.Os.version(),
            'os.kernel': System.Os.kernel_release(),
            'os.distributionName': System.Os.distribution_name(),
            'os.distributionId': System.Os.distribution_id(),
            'os.distributionVersion': System.Os.distribution_version(),
            'os.architecture': System.Os.architecture(),
            'hardware.cpu.architecture': System.Hardware.Cpu.architecture(),
            'hardware.cpu.logicalCoreCount': System.Hardware.Cpu.logical_core_count(),
            'hardware.cpu.physicalCoreCount': System.Hardware.Cpu.physical_core_count(),
            'hardware.disk.total': System.Hardware.Disk.total(),
            'hardware.disk.used': System.Hardware.Disk.used(),
            'hardware.disk.free': System.Hardware.Disk.free(),
            'hardware.disk.partitions': str(parts),
            'hardware.monitors': str(System.Hardware.monitors()),
            'hardware.screens': str(System.Hardware.screens()),
            'hardware.usbDevices': str(System.Hardware.usb_devices()),
            'hardware.printers': str(System.Hardware.printers()),
            'hardware.systemDefinitions': str(System.Hardware.system_definitions()),
            'hardware.model.version': str(System.Hardware.machine_model()),
            'hardware.memory.total': System.Hardware.Memory.total(),
            'hardware.network.ipAddresses': str(System.Hardware.Network.ip_addresses()),
            'sessions.userNames': str(System.Sessions.user_name()),
            'bios.releaseDate': System.BIOS.release_date()[1].replace('\n', '') if System.BIOS.release_date()[
                                                                                       0] == 0 else 'n/a',
            'bios.version': System.BIOS.version()[1].replace('\n', '') if System.BIOS.version()[0] == 0 else 'n/a',
            'bios.vendor': System.BIOS.vendor()[1].replace('\n', '') if System.BIOS.vendor()[0] == 0 else 'n/a',
            'hardware.baseboard.manufacturer': System.Hardware.BaseBoard.manufacturer()[1].replace('\n', '') if
            System.Hardware.BaseBoard.manufacturer()[0] == 0 else 'n/a',
            'hardware.baseboard.version': System.Hardware.BaseBoard.version()[1].replace('\n', '') if
            System.Hardware.BaseBoard.version()[0] == 0 else 'n/a',
            'hardware.baseboard.assetTag': System.Hardware.BaseBoard.asset_tag()[1].replace('\n', '') if
            System.Hardware.BaseBoard.asset_tag()[0] == 0 else 'n/a',
            'hardware.baseboard.productName': System.Hardware.BaseBoard.product_name()[1].replace('\n', '') if
            System.Hardware.BaseBoard.product_name()[0] == 0 else 'n/a',
            'hardware.baseboard.serialNumber': System.Hardware.BaseBoard.serial_number()[1].replace('\n', '') if
            System.Hardware.BaseBoard.serial_number()[0] == 0 else 'n/a',
        }

        return json.dumps(params)

    def unregister(self):
        self.logger.debug('Ahenk is unregistering...')
        self.db_service.delete('registration', ' 1==1 ')
        self.logger.debug('Ahenk is unregistered')

    def re_register(self):
        self.logger.debug('Reregistrating...')
        self.unregister()
        self.register(False)

    def generate_uuid(self, depend_mac=True):
        if depend_mac is False:
            self.logger.debug('uuid creating randomly')
            return uuid.uuid4()  # make a random UUID
        else:
            self.logger.debug('uuid creating according to mac address')
            return uuid.uuid3(uuid.NAMESPACE_DNS,
                              str(get_mac()))  # make a UUID using an MD5 hash of a namespace UUID and a mac address

    def generate_password(self):
        return uuid.uuid4()

    def registration_timeout(self):
        self.logger.error(
            'Could not reach registration response from Lider. Be sure XMPP server is reachable and it supports anonymous message, Lider is running properly '
            'and it is connected to XMPP server! Check your Ahenk configuration file (/etc/ahenk/ahenk.conf)')
        self.logger.error('Ahenk is shutting down...')
        print('Ahenk is shutting down...')
        #Util.show_message(os.getlogin(),':0',"Lider MYS sistemine ulaşılamadı. Lütfen sunucu adresini kontrol ediniz....","HATA")
        #System.Process.kill_by_pid(int(System.Ahenk.get_pid_number()))


    def clean(self):
        print('Ahenk cleaning..')
        import configparser
        try:
            config = configparser.ConfigParser()
            config._interpolation = configparser.ExtendedInterpolation()
            config.read(System.Ahenk.config_path())
            db_path = config.get('BASE', 'dbPath')

            if Util.is_exist(System.Ahenk.fifo_file()):
                Util.delete_file(System.Ahenk.fifo_file())

            if Util.is_exist(db_path):
                Util.delete_file(db_path)

            if Util.is_exist(System.Ahenk.pid_path()):
                Util.delete_file(System.Ahenk.pid_path())

            config.set('CONNECTION', 'uid', '')
            config.set('CONNECTION', 'password', '')
            config.set('MACHINE', 'user_disabled', '0')

            with open(System.Ahenk.config_path(), 'w') as file:
                config.write(file)
            file.close()
            print('Ahenk cleaned.')
        except Exception as e:
            self.logger.error("Error while running clean command. Error Message  " + str(e))
            print('Error while running clean command. Error Message {0}'.format(str(e)))
