import os
from dotenv import load_dotenv
from pyairtable import Api
from logger import Logger


class AirTable:
    def __init__(self, logger: Logger):
        load_dotenv()
        self._access_token = os.getenv("AIRTABLE_ACCESS_TOKEN")
        self._base_id = os.getenv("AIRTABLE_BASE_ID")
        self._inventory_table_id = os.getenv("AIRTABLE_INVENTORY_ID")
        self._people_table_id = os.getenv("AIRTABLE_PEOPLE_ID")
        self._api = Api(self._access_token)
        self._inventory_table = self._api.table(self._base_id, self._inventory_table_id)
        self._people_table = self._api.table(self._base_id, self._people_table_id)
        self._logger = logger

    @staticmethod
    def get_dict_differences(dict1, dict2):
        differences = [key for key in dict1.keys() if dict1[key] != dict2.get(key)]
        if "Employees" in differences:
            differences.remove("Employees")
        return differences

    @staticmethod
    def _process_row_info(row):
        data = row.get("fields")
        return data

    def _get_serial_numbers(self):
        table_data = self._inventory_table.all()
        output = {}
        for data in table_data:
            output[data.get("fields").get("Serial Number")] = data.get("id")
        return output

    def _get_all_names(self):
        table_data = self._people_table.all()
        all_fields = [row.get("fields") for row in table_data]
        return [row.get("name") for row in all_fields]

    def _get_all_employee_ids(self):
        table_data = self._people_table.all()
        output = {}
        for row in table_data:
            record_id = row.get("id")
            record_data = row.get("fields")
            output[record_data.get("employee_id")] = record_id
        return output

    def update_people_table(self, people_data):
        id_list = self._get_all_employee_ids()
        all_ids = id_list.keys()
        for person in people_data:
            employee_id = person.get("employee_id")
            if employee_id not in all_ids:
                self._logger.write_log(f"Added {person.get('name')} to the table")
                self._people_table.create(fields=person, typecast=True)
            else:
                record_id = id_list.get(employee_id)
                current_data = self._people_table.get(record_id).get("fields")
                differences = self.get_dict_differences(person, current_data)
                if len(differences) > 0:
                    self._logger.write_log(f"Update {person.get('name')} - {differences}")
                    new_data = {}
                    for key in differences:
                        new_data[key] = person[key]
                    self._people_table.update(record_id, fields=new_data, typecast=True)

    def update_inventory_table(self, inventory_data):
        serial_numbers = self._get_serial_numbers()
        all_serial_numbers = serial_numbers.keys()
        for device in inventory_data:
            serial_number = device.get("Serial Number")
            if serial_number not in all_serial_numbers:
                self._logger.write_log(f"Added Device: {device.get('Serial Number')}")
                self._inventory_table.create(fields=device, typecast=True)
            else:
                record_id = serial_numbers.get(serial_number)
                current_data = self._inventory_table.get(record_id).get(
                    "fields")

                differences = self.get_dict_differences(device, current_data)
                if len(differences) > 0:
                    self._logger.write_log(f"Update device: {device.get('Serial Number')} - {differences}")
                    new_data = {}
                    for key in differences:
                        new_data[key] = device[key]
                    self._inventory_table.update(record_id, fields=new_data,
                                                 typecast=True)
