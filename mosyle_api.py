import math
import os
import requests
import pytz
from datetime import datetime
from dotenv import load_dotenv

# TODO: Intune sync, Google sync, Refactor code to be cleaner and have
#  better documentation. Make this something that could be reused for other
#  clients


class MosyleAPI:
    def __init__(self):
        load_dotenv()
        self._base_url = "https://businessapi.mosyle.com/v1/"
        self._username = os.getenv("MOSYLE_USERNAME")
        self._password = os.getenv("MOSYLE_PASSWORD")
        self._access_token = os.getenv("MOSYLE_ACCESS_TOKEN")
        self._bearer_token = None

    @staticmethod
    def format_device(device):
        # TODO: Work on making this more accurate, rounded to the nearest
        #  logical value
        total_space = float(device.get("total_disk"))
        if total_space > 300:
            hd_space = math.ceil(total_space / 100) * 100
        else:
            hd_space = math.ceil(total_space / 10) * 10
        if hd_space >= 1000:
            hd = str(hd_space // 1000) + " TB"
        else:
            hd = str(hd_space) + " GB"

        os_number = int(device.get("osversion").split(".")[0])
        os_options = {
            10: "OSX",
            11: "Big Sur",
            12: "Monterey",
            13: "Ventura",
            14: "Sonoma"
        }

        # last_check_in = int(device.get('date_last_beat'))
        last_check_in = datetime.utcfromtimestamp(int(device.get("date_last_beat")))
        desired_timezone = pytz.timezone('US/Eastern')
        localized_datetime = pytz.utc.localize(last_check_in).astimezone(desired_timezone)

        output = {
            "HD Size": hd,
            "Serial Number": device.get("serial_number"),
            "Model": device.get("device_model_name"),
            "RAM": device.get("installed_memory") + " GB",
            "CPU": device.get("cpu_model"),
            "MacOS": os_options.get(os_number, "n/a"),
            "OS Version": device.get("osversion"),
            "Employees": device.get("username"),
            "Device Name": device.get("device_name"),
            "Enrolled In Mosyle": True,
            "Last Check In": localized_datetime.strftime(
                "%Y-%m-%dT%H:%M:%S.000Z")
        }
        # '2024-02-07T17:44:19.000Z'
        return output

    def api_login(self):
        url = self._base_url + "login"
        body = {
            "email": self._username,
            "password": self._password
        }
        headers = {
            "Content-Type": "application/json",
            "accesstoken": self._access_token
        }
        response = requests.post(url, headers=headers, json=body)
        if response.status_code == 200:
            bearer_token = response.headers["Authorization"]
            self._bearer_token = bearer_token

    def get_all_users(self):
        if not self._bearer_token:
            return

        url = self._base_url + 'users'
        headers = {
            "Content-Type": "application/json",
            "accesstoken": self._access_token,
            "Authorization": self._bearer_token
        }

        body = {
            "operation": "list_users",
            "options": {}
        }

        response = requests.post(url, headers=headers, json=body)
        data = response.json().get("response", [])
        return data

    def get_all_devices(self):
        if not self._bearer_token:
            return

        total_rows = math.inf
        current_page = 1
        output = []

        url = self._base_url + 'devices'
        headers = {
            "Content-Type": "application/json",
            "accesstoken": self._access_token,
            "Authorization": self._bearer_token
        }

        while 50 * (current_page - 1) < total_rows:

            body = {
                "operation": "list",
                "options": {
                    "os": "mac",
                    "page": current_page,
                    "specific_columns": [
                        "osversion",
                        "serial_number",
                        "device_name",
                        "device_model_name",
                        "total_disk",
                        "cpu_model",
                        "installed_memory",
                        'username',
                        'date_last_beat',
                    ]
                }
            }

            response = requests.post(url, headers=headers, json=body)
            data = response.json().get("response", [])
            if len(data) > 0:
                total_rows = data[0].get("rows")
                current_page += 1
                devices = data[0].get("devices")
                for device in devices:
                    output.append(self.format_device(device))

        return output
