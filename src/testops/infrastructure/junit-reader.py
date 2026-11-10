from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree

from testops.domain.models import TestResult, TestStatus


class JUnitResultReader:
    """Reads JUnit XML reports into canonical TestOps test results."""

    def __init__(self, report_path: Path) -> None:
        self._report_path = report_path

    def read(self) -> list[TestResult]:
        root = ElementTree.parse(self._report_path).getroot()

        return [
            self._to_test_result(testcase)
            for testcase in root.iter("testcase")
        ]

    @staticmethod
    def _to_test_result(testcase: ElementTree.Element) -> TestResult:
        classname = testcase.attrib.get("classname", "unknown")
        name = testcase.attrib["name"]
        duration = float(testcase.attrib.get("time", "0"))

        status = JUnitResultReader._status_of(testcase)

        return TestResult(
            test_id=f"{classname}::{name}",
            status=status,
            duration_ms=duration * 1000,
        )

    @staticmethod
    def _status_of(testcase: ElementTree.Element) -> TestStatus:
        if testcase.find("failure") is not None:
            return TestStatus.FAILED

        if testcase.find("error") is not None:
            return TestStatus.FAILED

        if testcase.find("skipped") is not None:
            return TestStatus.SKIPPED

        return TestStatus.PASSED