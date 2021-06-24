from unittest.mock import patch

import pandas as pd

from pykusto import Query, PySparkKustoClient
from test.test_base import TestBase


class MockDataFrameReader:
    def __init__(self, dataframe_to_return: pd.DataFrame) -> None:
        self.format = None
        self.options = {}
        self.dataframe_to_return = dataframe_to_return

    def format(self, the_format: str) -> 'MockDataFrameReader':
        assert self.format is None, "Trying to set format twice"
        self.format = the_format
        return self

    def option(self, key: str, value: str) -> 'MockDataFrameReader':
        assert key not in self.options, f"Trying to set option '{key}' twice"
        self.options[key] = value
        return self

    def load(self) -> pd.DataFrame:
        return self.dataframe_to_return


class MockSparkSession:
    def __init__(self, dataframe_to_return: pd.DataFrame) -> None:
        self.read = MockDataFrameReader(dataframe_to_return)


class TestClient(TestBase):
    def test_linked_service(self):
        rows = (['foo', 10], ['bar', 20], ['baz', 30])
        columns = ('stringField', 'numField')
        expected_df = pd.DataFrame(rows, columns=columns)
        mock_spark_session = MockSparkSession(expected_df)

        with patch('pykusto._src.pyspark_client.PySparkKustoClient.get_spark_session', lambda s: mock_spark_session):
            client = PySparkKustoClient('https://help.kusto.windows.net/', linked_service='MockLinkedKusto', fetch_by_default=False)

        table = client['test_db']['mock_table']
        actual_df = Query(table).take(5).to_dataframe()
        self.assertTrue(expected_df.equals(actual_df))

        self.assertEqual('com.microsoft.kusto.spark.synapse.datasource', mock_spark_session.read.format)
        self.assertEqual(
            {
                'spark.synapse.linkedService': 'MockLinkedKusto',
                'kustoDatabase': 'test_db',
                'kustoQuery': 'mock_table | take 5',
            },
            mock_spark_session.read.options,
        )
