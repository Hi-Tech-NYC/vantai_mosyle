import json


class HiBob:
    def __init__(self):
        self._output_data = []
        self._json_file = "./bob_staff.json"

    def process_json(self):
        with open(self._json_file) as the_file:
            data = json.load(the_file)["result"]
            self._process_block(data)

    def get_people_info(self):
        return self._output_data

    def get_people_names(self):
        output = [person.get("name") for person in self._output_data]
        return output

    def _format_data(self, data):
        displayName = data.get("displayName", "n/a")
        title = data.get("/work/title", {}).get("humanReadable", "n/a")
        department = data.get("/work/department", {}).get("humanReadable", "n/a")
        location = data.get("/work/siteId", {}).get("humanReadable", "n/a")
        output = {
            "name": displayName,
            "title": title,
            "department": department,
            "location": location

        }
        self._output_data.append(output)

    def _process_block(self, block):
        self._format_data(block.get("data"))
        if len(block.get("children", [])) > 0:
            for child in block.get("children", []):
                self._process_block(child)
