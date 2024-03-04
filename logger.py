import os
from datetime import datetime


class Logger:
    def __init__(self):
        self._log_name = f"{datetime.now().isoformat()}"
        self._script_directory = os.path.dirname(os.path.abspath(__file__))
        self._directory = os.path.join(self._script_directory,
                                       'logs')

    def write_log(self, message):
        print(message)
        if not os.path.exists(self._directory):
            os.makedirs(self._directory)
        with open(f"{self._directory}/{self._log_name}.log", "a") as the_file:
            the_file.write(f"{message}\n")
