import os
import dotenv
import requests


class HiBob:
    def __init__(self):
        dotenv.load_dotenv()
        self._output_data = []
        self._bob_user = os.getenv("BOB_USERNAME")
        self._bob_password = os.getenv("BOB_PASSWORD")

    def get_bob_data(self):
        url = ("https://api.hibob.com/v1/people?humanReadable=true"
               "&includeHumanReadable=false")
        headers = {"accept": "application/json"}
        response = requests.get(url, headers=headers, auth=(self._bob_user, self._bob_password))
        json_data = response.json()
        if response.status_code == 200:
            employees = json_data.get("employees")
            for employee in employees:
                self._format_data(employee)

    def get_people_info(self):
        return self._output_data

    @staticmethod
    def format_date(date):
        date_array = date.split("/")
        return f"{date_array[2]}-{date_array[1]}-{date_array[0]}"

    def _format_data(self, data):
        displayName = data.get("displayName", "n/a")
        work_stuff = data.get("work", {})
        title = work_stuff.get("title", "n/a")
        department = work_stuff.get("department", "n/a")
        location = work_stuff.get("site", "n/a")
        email = data.get("email", "n/a")
        employee_id = data.get("id", "n/a")
        start_date = self.format_date(work_stuff.get("startDate", "n/a"))
        output = {
            "employee_id": employee_id,
            "name": displayName,
            "title": title,
            "department": department,
            "location": location,
            "email": email,
            "start_date": start_date,
        }
        self._output_data.append(output)
