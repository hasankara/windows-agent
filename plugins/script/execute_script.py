#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Emre Akkaya <emre.akkaya@agem.com.tr>

from base.plugin.abstract_plugin import AbstractPlugin
import json


class ExecuteScript(AbstractPlugin):
    def __init__(self, data, context):
        super(AbstractPlugin, self).__init__()
        self.data = data
        self.context = context
        self.logger = self.get_logger()
        self.message_code = self.get_message_code()

        self.temp_file_name = str(self.generate_uuid())
        self.base_file_path = '{0}{1}'.format(str(self.Ahenk.received_dir_path()), self.temp_file_name)

    def handle_task(self):
        try:
            script_type = self.data['SCRIPT_TYPE']
            script_contents = self.format_contents(self.data['SCRIPT_CONTENTS'])
            script_params = self.data['SCRIPT_PARAMS']
            file_path = self.base_file_path

            # Determine script extension and command
            command = ''
            # if script_type == 'BASH':
            #     file_path += '.sh'
            #     command += 'bash'
            # elif script_type == 'PYTHON':
            #     file_path += '.py'
            #     command += 'python'
            # elif script_type == 'PERL':
            #     file_path += '.pl'
            #     command += 'perl'
            # elif script_type == 'RUBY':
            #     file_path += '.rb'
            #     command += 'ruby'

            # for windows
            file_path += '.ps1'
            command = "'r'powershell.exe', '-ExecutionPolicy', 'Unrestricted'"

            self.logger.error("code  will be written here for windows power shell!!!!!!!!")
            self.create_script_file(file_path, script_contents)
            #
            # result_code, p_out, p_err = self.execute_script_file(command, file_path, script_params)
            # if result_code != 0:
            #     self.logger.error("Error occurred while executing script: " + str(p_err))
            #     self.context.create_response(code=self.message_code.TASK_ERROR.value,
            #                                  message='Betik çalıştırılırken hata oluştu',
            #                                  data=json.dumps({'Result': p_err}),
            #                                  content_type=self.get_content_type().APPLICATION_JSON.value)
            # else:
            #     self.logger.debug("Executed script file.")
            #     self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
            #                                  message='Betik başarıyla çalıştırıldı.',
            #                                  data=json.dumps({'Result': p_out}),
            #                                  content_type=self.get_content_type().APPLICATION_JSON.value)
            result_code, p_out, p_err = self.execute_script_file(file_path, script_params)
            if result_code != 0:
                self.logger.error("Error occurred while executing script: " + str(p_err))
                self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                             message='Betik çalıştırılırken hata oluştu',
                                             data=json.dumps({'Result': p_err}),
                                             content_type=self.get_content_type().APPLICATION_JSON.value)
            else:
                self.logger.debug("Executed script file.")
                self.context.create_response(code=self.message_code.TASK_PROCESSED.value,
                                             message='Betik başarıyla çalıştırıldı.',
                                             data=json.dumps({'Result': p_out}),
                                             content_type=self.get_content_type().APPLICATION_JSON.value)
        except Exception as e:
            self.logger.error(str(e))
            self.context.create_response(code=self.message_code.TASK_ERROR.value,
                                         message='Betik çalıştırılırken hata oluştu:' + str(e),
                                         content_type=self.get_content_type().APPLICATION_JSON.value)

    def create_script_file(self, file_path, script_contents):
        self.logger.debug("Creating script file.")
        # Create temporary script file with the provided content
        self.write_file(file_path, script_contents)

        # Make the file executable
        # self.make_executable(file_path)
        self.logger.debug("Created script file: {0}".format(file_path))

    def execute_script_file(self, file_path, script_params):
        self.logger.debug("Executing script file.")
        # Execute the file
        if not script_params:
            return self.execute_win_command(file_path)
        else:
            param_str = ""
            for params in script_params.split(" "):
                param_str += '"' + params + '" '
            return self.execute_win_command(file_path, param_str[:-1])

    @staticmethod
    def format_contents(contents):
        # will be edited for windows if needed
        # tmp = contents
        # replacements = list()
        # replacements.append(('&dbq;', '\"'))
        # replacements.append(('&sgq;', '\''))
        # for r, n in replacements:
        #     tmp = tmp.replace(r, n)
        # return tmp
        return contents


def handle_task(task, context):
    plugin = ExecuteScript(task, context)
    plugin.handle_task()
