import pandas as pd
import requests
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class EntityProcessor:
    def process(self, json_data: list) -> pd.DataFrame:
        """Метод для обробки даних. Реалізується в дочірніх класах."""
        pass


class PeopleProcessor(EntityProcessor):
    def process(self, json_data: list) -> pd.DataFrame:
        df = pd.DataFrame(json_data)
        df['full_name'] = df['name']
        logger.info("Обробка сутностей 'people'")
        return df


class PlanetsProcessor(EntityProcessor):
    def process(self, json_data: list) -> pd.DataFrame:
        df = pd.DataFrame(json_data)
        df['population'] = pd.to_numeric(df['population'], errors='coerce')
        logger.info("Обробка сутностей 'planets'")
        return df


class SWAPIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def fetch_json(self, endpoint: str) -> list:
        url = f"{self.base_url}{endpoint}"
        all_data = []

        while url:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            all_data.extend(data['results'])
            url = data.get('next')

        return all_data


class SWAPIDataManager:
    def __init__(self, client: SWAPIClient):
        self.client = client
        self.processors = {}

    def register_processor(self, endpoint: str, processor: EntityProcessor):
        self.processors[endpoint] = processor

    def fetch_entity(self, endpoint: str) -> pd.DataFrame:
        logger.info(f"Завантаження даних для: {endpoint}")
        json_data = self.client.fetch_json(endpoint)

        if endpoint not in self.processors:
            logger.warning(f"Процесор для '{endpoint}' не зареєстрований")
            return pd.DataFrame(
                json_data)

        processor = self.processors[endpoint]
        return processor.process(json_data)

    def save_to_excel(self, filename: str):
        with pd.ExcelWriter(filename) as writer:
            for endpoint, processor in self.processors.items():
                logger.info(f"Збереження даних для {endpoint} в Excel")
                df = self.fetch_entity(endpoint)
                sheet_name = endpoint.rstrip('/')
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        logger.info("Дані успішно збережено в Excel")


if __name__ == "__main__":
    client = SWAPIClient("https://swapi.dev/api/")
    data_manager = SWAPIDataManager(client)

    data_manager.register_processor("people", PeopleProcessor())
    data_manager.register_processor("planets", PlanetsProcessor())

    data_manager.save_to_excel("swapi_data.xlsx")
