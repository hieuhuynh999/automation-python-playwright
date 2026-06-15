from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

PRIORITY_MARKERS = frozenset({"critical", "high", "medium", "low"})


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

    @staticmethod
    def _to_pytest_param(row: dict[str, Any], index: int) -> pytest.ParameterSet:
        marks: list[Any] = []
        priority = str(row.get("priority", "")).strip().lower()

        if priority in PRIORITY_MARKERS:
            marks.append(getattr(pytest.mark, priority))

        param_id = row.get("test_case_id") or f"case{index + 1}"
        return pytest.param(row, marks=marks, id=param_id)

    @staticmethod
    def parametrize(application: str, test_method: str) -> list[pytest.ParameterSet]:
        rows = DataProvider.get_data(application, test_method)
        return [
            DataProvider._to_pytest_param(row, index)
            for index, row in enumerate(rows)
        ]

    # ======================
    # EFMS
    # ======================

    @staticmethod
    def efms(
        test_method: str,
    ):
        return DataProvider.get_data(
            "efms",
            test_method,
        )

    @staticmethod
    def efms_cases(test_method: str) -> list[pytest.ParameterSet]:
        return DataProvider.parametrize("efms", test_method)

    # ======================
    # ETMS
    # ======================

    @staticmethod
    def etms(
        test_method: str,
    ):
        return DataProvider.get_data(
            "etms",
            test_method,
        )

    @staticmethod
    def etms_cases(test_method: str) -> list[pytest.ParameterSet]:
        return DataProvider.parametrize("etms", test_method)