import pandas as pd
import requests
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class SWAPIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def fetch_json(self, endpoint: str) -> list:
        url = f"{self.base_url}{endpoint}"
        all_data = []

        while url:
            logger.info(f"Отримання даних з: {url}")
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            all_data.extend(data['results'])
            url = data.get('next')

        return all_data


class DataHandler:
    def __init__(self, client: SWAPIClient):
        self.client = client
        self.data_frames = {}

    def fetch_and_store_data(self, endpoint: str):
        logger.info(f"Завантаження даних для {endpoint}")
        json_data = self.client.fetch_json(endpoint)
        self.data_frames[endpoint] = pd.DataFrame(json_data)

    def remove_columns(self, endpoint: str, columns: list):
        if endpoint in self.data_frames:
            logger.info(f"Видалення стовпців {columns} з {endpoint}")
            self.data_frames[endpoint].drop(columns=columns, inplace=True)
        else:
            logger.warning(f"Не знайдено даних для {endpoint}")


class ExcelExporter:
    def __init__(self, data_handler: DataHandler):
        self.data_handler = data_handler

    def export_to_excel(self, filename: str):
        logger.info(f"Запис даних у файл: {filename}")
        with pd.ExcelWriter(filename) as writer:
            for endpoint, df in self.data_handler.data_frames.items():
                sheet_name = endpoint.rstrip('/')
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        logger.info("Дані успішно збережено в Excel")


if __name__ == "__main__":
    client = SWAPIClient("https://swapi.dev/api/")
    data_handler = DataHandler(client)

    # Завантаження і обробка даних
    for endpoint in ["people", "planets"]:
        data_handler.fetch_and_store_data(endpoint)

    # Видалення непотрібних стовпців
    data_handler.remove_columns("people", ["films", "species"])

    # Збереження даних в Excel
    excel_exporter = ExcelExporter(data_handler)
    excel_exporter.export_to_excel("swapi_data_restructured.xlsx")
