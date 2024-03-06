import csv
import inspect
import os
import pprint
import logging
from pathlib import Path
from typing import Any, Dict

import inflection
from masoniteorm.migrations import Migration
from masoniteorm.query import QueryBuilder

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Fixture:
    def mount(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__connection__ = inflection.pluralize(self.__class__.__name__.lower())
        self.__table__ = inflection.pluralize(self.__class__.__name__.lower())
        self.__resource__ = inflection.pluralize(self.__class__.__name__.lower())
        logger.info(f"Initializing [{self.__resource__}] Fixture")

        self.connection()
        return QueryBuilder().on(f'{self.__resource__}').table(f'{self.__resource__}')

    def connection(self) -> Any:
        logger.info(f"Connecting to [{self.__resource__}] Fixture")
        from config.database import DATABASES, DB
        cache_path = Path(inspect.getfile(self.__class__)).parent / "fixture-cache"
        cache_path.mkdir(exist_ok=True)
        cache_file = cache_path / f"{self.__resource__}.sqlite3"
        self.cache_file_dir = cache_path / cache_file
        if not cache_file.exists():
            cache_file.touch()
        DATABASES.update({
            f'{self.__resource__}': {
                "driver": "sqlite",
                "database": cache_file,
                "log_queries": True,
            }
        })
        DB.set_connection_details(DATABASES)

        self.create_table()
        self.check_data_freshness()
        return self

    def create_table(self):
        logger.info(f"Creating [{self.__resource__}] Fixture Table")
        table_name: str = self.__resource__
        create_table: Migration = Migration(connection=table_name)

        if getattr(self, "get_rows", None):
            first_row: dict[str, Any] = self.get_rows()[0]

        if getattr(self, "rows", None):
            first_row: dict[str, Any] = self.rows[0]

        if not getattr(self, 'rows', None) and not getattr(self, 'get_rows', None):
            raise AttributeError(
                f"[rows] attribute or [get_rows] method must be defined on the model [{self.__class__.__name__}]")

        try:
            with create_table.schema.create(table_name) as table:
                table.increments("id")
                for key, value in first_row.items():
                    if key == "id":
                        continue
                    if isinstance(value, int):
                        table.integer(key).nullable()
                    elif isinstance(value, str):
                        table.string(key).nullable()
                    elif isinstance(value, float):
                        table.float(key).nullable()
                    elif isinstance(value, bool):
                        table.boolean(key).nullable()
                    else:
                        table.string(key).nullable()
                table.timestamps()
        except Exception as e:
            return None

    def migrate(self):
        logger.info(f"Migrating [{self.__resource__}] Fixture Data")
        if getattr(self, "get_rows", None):
            QueryBuilder().on(f'{self.__resource__}').table(f'{self.__resource__}').bulk_create(
                self.get_rows()
            )
            return self

        if getattr(self, "rows", None):
            QueryBuilder().on(f'{self.__resource__}').table(f'{self.__resource__}').bulk_create(
                self.rows
            )
            return self

        raise AttributeError(
            f"[rows] attribute or [get_rows] method must be defined on the model [{self.__class__.__name__}]")

    def check_data_freshness(self):
        logger.info(f"Checking [{self.__resource__}] Fixture Data Freshness")
        cache_path = Path(inspect.getfile(self.__class__)).parent / "fixture-cache"
        cache_file = cache_path / f"{self.__resource__}.sqlite3"
        cache_file_dir = cache_path / cache_file
        cache_file_last_updated = os.path.getmtime(cache_file_dir)
        model_file_last_updated = os.path.getmtime(inspect.getfile(self.__class__))

        logger.info(
            f"Cache file last updated: {cache_file_last_updated}, Model file last updated: {model_file_last_updated}")

        # If the cache file is older than the model file, then we need to refresh the data
        if cache_file_last_updated > model_file_last_updated:
            QueryBuilder().on(f'{self.__resource__}').table(f'{self.__resource__}').delete()
            self.migrate()
        return self

    def csv_to_list_dicts(self, csv_path: str):
        myFile = open(csv_path, "r")
        reader = csv.DictReader(myFile)
        myList = list()
        for dictionary in reader:
            myList.append(dictionary)
        return myList

    def get_schema(self):
        return self.schema
