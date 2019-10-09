"""import time
import random
from pathlib import Path
from src.SMWinservice import SMWinservice
from base.logger.ahenk_logger import Logger
from base.scope import Scope

class AhenkDaemon(SMWinservice):


    # windows service parameters
    _svc_name_ = "Ahenk"
    _svc_display_name_ = "LiderAhenk Agent"
    _svc_description_ = "Ahenk Service"

    def start(self):
        self.isrunning = True

    def stop(self):
        self.isrunning = False

    @staticmethod
    def init_logger():

        logger = Logger()
        logger.info('Log was set')
        Scope.get_instance().set_logger(logger)
        return logger

    def main(self):
        i = 0
        while self.isrunning:
            random.seed()
            x = random.randint(1, 1000000)
            Path(f'C:\\Users\\hasan\\Desktop\\test\\ahenk_{x}.txt').touch()
            time.sleep(5)
            # print(x)

if __name__ == '__main__':
    AhenkDaemon.parse_command_line()
"""