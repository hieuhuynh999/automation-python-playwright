from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class DataProvider:

    BASE_PATH = (
        Path(__file__)
        .parent
        / "testdata"
    )


    @staticmethod
    def load_file(
        file_name: str
    ) -> dict[str, Any]:
        """
        Load json data file

        Example:
            dataTest-efms.json
            dataTest-etms.json
        """

        file_path = (
            DataProvider.BASE_PATH /
            file_name
        )

        if not file_path.exists():
            raise FileNotFoundError(
                f"Test data not found: {file_path}"
            )


        with open(
            file_path,
            encoding="utf-8"
        ) as file:

            return json.load(file)



    @staticmethod
    def get_data(
        application: str,
        test_method: str
    ) -> list[dict[str, Any]]:
        """
        Get test data by application and test method

        Example:
            DataProvider.get_data(
                "efms",
                "test_login_efms"
            )
        """


        file_mapping = {

            "efms": "dataTest-efms.json",

            "etms": "dataTest-etms.json",

        }


        if application not in file_mapping:
            raise ValueError(
                f"Unsupported application: {application}"
            )


        data = DataProvider.load_file(
            file_mapping[application]
        )


        if test_method not in data:
            raise KeyError(
                f"Cannot find {test_method} "
                f"in {file_mapping[application]}"
            )


        return data[test_method]



    # ======================
    # EFMS
    # ======================

    @staticmethod
    def efms(
        test_method: str
    ):

        return DataProvider.get_data(
            "efms",
            test_method
        )



    # ======================
    # ETMS
    # ======================

    @staticmethod
    def etms(
        test_method: str
    ):

        return DataProvider.get_data(
            "etms",
            test_method
        )