import os
import queue
import signal
import sys
import threading
import time

from glob import glob
from base.logger.ahenk_logger import Logger
from base.scope import Scope
from base.config.config_manager import ConfigManager
from base.system.system import System
from base.database.ahenk_db_service import AhenkDbService
from base.messaging.messaging import Messaging
from base.registration.registration import Registration
from base.event.event_manager import EventManager
from base.messaging.messenger import Messenger
from base.command.command_manager import Commander
from base.command.command_runner import CommandRunner
from base.task.task_manager import TaskManager
from base.plugin.plugin_manager_factory import PluginManagerFactory
from base.execution.execution_manager import ExecutionManager
from base.messaging.message_response_queue import MessageResponseQueue
from base.scheduler.scheduler_factory import SchedulerFactory
import codecs
ahenk_daemon = None


class AhenkDaemon:
    """Ahenk service base class which initializes services and maintains events/commands"""

    @staticmethod
    def reload():
        """ docstring"""
        # reload service here
        pass

    @staticmethod
    def init_logger():
        """ docstring"""
        print('init logger...')
        logger = Logger()
        logger.info('Log was set')
        Scope.get_instance().set_logger(logger)
        return logger

    @staticmethod
    def init_config_manager(config_file_path, configfile_folder_path):
        """ docstring"""
        config_manager = ConfigManager(config_file_path, configfile_folder_path)
        config = config_manager.read()
        Scope.get_instance().set_configuration_manager(config)
        return config

    @staticmethod
    def init_event_manager():
        """ docstring"""
        event_manager = EventManager()
        Scope.get_instance().set_event_manager(event_manager)
        return event_manager

    @staticmethod
    def init_ahenk_db():
        """ docstring"""
        db_service = AhenkDbService()
        db_service.connect()
        db_service.initialize_table()
        Scope.get_instance().set_sb_service(db_service)
        return db_service

    @staticmethod
    def init_messaging():
        """ docstring"""
        message_manager = Messaging()
        Scope.get_instance().set_message_manager(message_manager)
        return message_manager

    @staticmethod
    def init_registration():
        """ docstring"""
        registration = Registration()
        Scope.get_instance().set_registration(registration)
        return registration

    @staticmethod
    def init_execution_manager():
        """ docstring"""
        execution_manager = ExecutionManager()
        Scope.get_instance().set_execution_manager(execution_manager)
        return execution_manager

    def check_registration(self):
        """ docstring"""
        # max_attempt_number = int(System.Hardware.Network.interface_size()) * 3
        max_attempt_number = 1
        # self.logger.debug()
        # logger = Scope.getInstance().getLogger()
        registration = Scope.get_instance().get_registration()

        try:
            #if registration.is_registered() is False:
            #    self.logger.debug('Ahenk is not registered. Attempting for registration')
            #    if registration.registration_request() == False:
            #        self.registration_failed()

            if registration.is_registered() is False:
                print("Registration attemp")
                max_attempt_number -= 1
                self.logger.debug('Ahenk is not registered. Attempting for registration')
                # registration.registration_request(self.register_hostname,self.register_user_name,self.register_user_password)
                registration.registration_request(None, None, None)
                #if max_attempt_number < 0:
                #    self.logger.warning('Number of Attempting for registration is over')
                #    self.registration_failed()
                #    break
        except Exception as e:
            self.registration_failed()
            self.logger.error('Registration failed. Error message: {0}'.format(str(e)))

    def is_registered(self):
        try:
            registration = Scope.get_instance().get_registration()
            if registration.is_registered() is False:
                self.registration_failed()

        except Exception as e:
            self.registration_failed()
            self.logger.error('Registration failed. Error message: {0}'.format(str(e)))

    def registration_failed(self):
        """ docstring"""
        self.logger.error('Registration failed. All registration attempts were failed. Ahenk is stopping...')
        print('Registration failed. Ahenk is stopping..')
        # ahenk_daemon.stop()

    @staticmethod
    def init_messenger():
        """ docstring"""
        messenger_ = Messenger()
        messenger_.connect_to_server()
        Scope.get_instance().set_messenger(messenger_)
        return messenger_

    def init_signal_listener(self):
        """ docstring"""
        try:
            signal.signal(signal.SIGALRM, CommandRunner().run_command_from_fifo)
            self.logger.info('Signal handler is set up')
        except Exception as e:
            self.logger.error('Signal handler could not set up. Error Message: {0} '.format(str(e)))

    @staticmethod
    def init_plugin_manager():
        """ docstring"""
        plugin_manager = PluginManagerFactory.get_instance()
        Scope.get_instance().set_plugin_manager(plugin_manager)
        # order changed, problem?
        plugin_manager.load_plugins()
        return plugin_manager

    @staticmethod
    def init_task_manager():
        """ docstring"""
        task_manager = TaskManager()
        Scope.get_instance().set_task_manager(task_manager)
        return task_manager

    @staticmethod
    def init_message_response_queue():
        """ docstring"""
        response_queue = queue.Queue()
        message_response_queue = MessageResponseQueue(response_queue)
        message_response_queue.setDaemon(True)
        message_response_queue.start()
        Scope.get_instance().set_response_queue(response_queue)
        return response_queue

    @staticmethod
    def init_scheduler():
        """ docstring"""
        scheduler_ins = SchedulerFactory.get_intstance()
        scheduler_ins.initialize()
        Scope.get_instance().set_scheduler(scheduler_ins)
        sc_thread = threading.Thread(target=scheduler_ins.run)
        sc_thread.setDaemon(True)
        sc_thread.start()
        return scheduler_ins

    def run(self):
        """ docstring"""
        print('Ahenk running...')

        global_scope = Scope()
        global_scope.set_instance(global_scope)

        config_file_folder_path = 'C:\\Users\\hasan\\ahenk\\'

        # configuration manager must be first load
        self.init_config_manager(System.Ahenk.config_path(), config_file_folder_path)

        # Logger must be second
        self.logger = self.init_logger()
        self.logger.info('Pid file was created')
        print("logger is set")
        # print("dsadasişşğşüğşşüğşğşüğ")
        self.logger.info('şiğüğüğüşğüşüğşüğşüğşüğşüğşüğ'.encode().decode('utf-8'))

        self.init_event_manager()
        self.logger.info('Event Manager was set')

        self.init_ahenk_db()
        self.logger.info('DataBase Service was set')

        self.init_messaging()
        self.logger.info('Message Manager was set')

        self.init_plugin_manager()
        self.logger.info('Plugin Manager was set')

        self.init_scheduler()
        self.logger.info('Scheduler was set')

        self.init_task_manager()
        self.logger.info('Task Manager was set')

        self.init_registration()
        self.logger.info('Registration was set')

        self.init_execution_manager()
        self.logger.info('Execution Manager was set')

        self.check_registration()

        self.messenger = self.init_messenger()
        self.logger.info('Messenger was set')

        self.init_signal_listener()
        self.logger.info('Signals listeners was set')

        self.init_message_response_queue()

        while True:
            time.sleep(1)


if __name__ == '__main__':
    print("hello")


    ahenk_daemon = AhenkDaemon()
    while True:
        ahenk_daemon.run()
