#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Volkan Şahin <volkansah.in> <bm.volkansahin@gmail.com>

import json
import time
from multiprocessing import Process

from base.command.command_manager import Commander
from base.scope import Scope
from base.system.system import System
from base.timer.setup_timer import SetupTimer
from base.timer.timer import Timer
from base.util.util import Util


class CommandRunner(object):
    def __init__(self):
        scope = Scope().get_instance()
        self.logger = scope.get_logger()
        self.plugin_manager = scope.get_plugin_manager()
        self.message_manager = scope.get_message_manager()
        self.messenger = scope.get_messenger()
        self.conf_manager = scope.get_configuration_manager()
        self.db_service = scope.get_db_service()
        self.execute_manager = scope.get_execution_manager()

    def check_last_login(self):
        last_login_tmstmp = self.db_service.select_one_result('session', 'timestamp')
        if not last_login_tmstmp:
            return True

        if (int(time.time()) - int(last_login_tmstmp)) < 10:
            return False
        else:
            return True

    def delete_polkit_user(self):
        content = "[Configuration] \nAdminIdentities=unix-user:root"
        ahenk_policy_file = "/etc/polkit-1/localauthority.conf.d/99-ahenk-policy.conf"
        if not Util.is_exist(ahenk_policy_file):
            self.logger.info('Ahenk polkit file not found')
        else:
            Util.delete_file(ahenk_policy_file)
            Util.write_file(ahenk_policy_file, content)
            self.logger.info('Root added ahenk polkit file')

    def run_command_from_fifo(self, num, stack):
        """ docstring"""

        while True:
            try:
                event = Commander().get_event()
                if event is None:
                    break
                json_data = json.loads(event)
            except Exception as e:
                self.logger.error(
                    'A problem occurred while loading json. Check json format! Error Message: {0}.'
                    ' Event = {1}'.format(str(e), str(event)))
                return

            if json_data is not None:

                self.logger.debug('Signal handled')
                self.logger.debug('Signal is :{0}'.format(str(json_data['event'])))

                if str(json_data['event']) == 'login' and self.check_last_login():
                    username = json_data['username']
                    display = json_data['display']
                    desktop = json_data['desktop']

                    ip = None
                    if 'ip' in json_data:
                        ip = json_data['ip']

                    self.logger.info('login event is handled for user: {0}'.format(username))
                    Util.execute("systemctl restart sssd.service")
                    login_message = self.message_manager.login_msg(username,ip)
                    self.messenger.send_direct_message(login_message)


                elif str(json_data['event']) == 'logout':
                    username = json_data['username']
                    self.db_service.delete('session', 'username=\'{0}\''.format(username))
                    self.execute_manager.remove_user_executed_policy_dict(username)
                    # TODO delete all user records while initializing
                    self.logger.info('logout event is handled for user: {0}'.format(username))
                    ip = None
                    if 'ip' in json_data:
                        ip = json_data['ip']
                    logout_message = self.message_manager.logout_msg(username,ip)
                    self.messenger.send_direct_message(logout_message)

                    self.logger.info('Ahenk polkit file deleting..')
                    self.delete_polkit_user()

                    self.plugin_manager.process_mode('logout', username)
                    self.plugin_manager.process_mode('safe', username)

                elif str(json_data['event']) == 'send':
                    self.logger.info('Sending message over ahenkd command. Response Message: {0}'.format(
                        json.dumps(json_data['message'])))
                    message = json.dumps(json_data['message'])
                    self.messenger.send_direct_message(message)

                elif str(json_data['event']) == 'unregister':
                    self.logger.info('Unregistering..')
                    unregister_message = self.message_manager.unregister_msg()
                    if unregister_message is not None:
                        self.messenger.send_direct_message(unregister_message)

                elif str(json_data['event']) == 'load':
                    plugin_name = str(json_data['plugins'])

                    if plugin_name == 'all':
                        self.logger.debug('All plugins are loading to ahenk')
                        self.plugin_manager.load_plugins()
                    else:
                        for p_name in plugin_name.split(','):
                            self.logger.debug('{0} plugin is loading to ahenk'.format(p_name))
                            self.plugin_manager.load_single_plugin(p_name)

                elif str(json_data['event']) == 'reload':
                    plugin_name = str(json_data['plugins'])

                    if plugin_name == 'all':
                        self.logger.debug('All plugins are reloading to ahenk')
                        self.plugin_manager.reload_plugins()
                    else:
                        for p_name in plugin_name.split(','):
                            self.logger.debug('{0} plugin is reloading to ahenk'.format(p_name))
                            self.plugin_manager.reload_single_plugin(p_name)

                elif str(json_data['event']) == 'remove':
                    plugin_name = str(json_data['plugins'])

                    if plugin_name == 'all':
                        self.logger.debug('All plugins are removing from ahenk')
                        self.plugin_manager.remove_plugins()
                    else:
                        for p_name in plugin_name.split(','):
                            self.logger.debug('{0} plugin is removing from ahenk'.format(p_name))
                            self.plugin_manager.remove_single_plugin(p_name)

                elif str(json_data['event']) == 'stop':
                    self.plugin_manager.process_mode('shutdown')
                    self.logger.info('Shutdown mode activated.')

                    # TODO timeout
                    while self.running_plugin() is False:
                        self.logger.debug('Waiting for progress of plugins...')
                        time.sleep(0.5)

                    Util.delete_file(System.Ahenk.fifo_file())
                    Scope().get_instance().get_custom_param('ahenk_daemon').stop()
                else:
                    self.logger.error('Unknown command error. Command:' + json_data['event'])
                self.logger.debug('Processing of handled event is completed')

    def running_plugin(self):
        """ docstring"""
        for plugin in self.plugin_manager.plugins:
            if plugin.keep_run is True:
                return False
        return True
