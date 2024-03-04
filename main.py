from mosyle_api import MosyleAPI
from airtable import AirTable
from bob import HiBob
from logger import Logger
import time

if __name__ == "__main__":
    logger = Logger()
    start_time = time.time()
    logger.write_log(f"Starting at {time.ctime()}")

    bob = HiBob()
    bob.process_json()
    all_people = bob.get_people_info()

    airtable = AirTable(logger=logger)
    airtable.update_people_table(all_people)

    mosyle_api = MosyleAPI()
    mosyle_api.api_login()
    all_devices = mosyle_api.get_all_devices()
    airtable.update_inventory_table(all_devices)

    logger.write_log(f"Finished in {round((time.time() - start_time), 2)} seconds")
