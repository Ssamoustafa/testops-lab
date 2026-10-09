from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree

from testops.domain.models import TestResult, TestStatus


class JUnitReportError(Exception):
    """Raised when a JUnit report cannot be read or interpreted."""


class JUnitResultReader:
    """Translate JUnit XML reports into canonical TestOps results."""

    def __init__(self, report_path: Path) -> None:
        self._report_path = report_path

    def read(self) -> list[TestResult]:
        try:
            root = ElementTree.parse(self._report_path).getroot()
        except (ElementTree.ParseError, OSError) as exc:
            raise JUnitReportError(f"Unable to read JUnit report: {self._report_path}") from exc

        return [self._to_test_result(testcase) for testcase in root.iter("testcase")]

    @staticmethod
    def _to_test_result(
        testcase: ElementTree.Element,
    ) -> TestResult:
        name = testcase.attrib.get("name")

        if not name or not name.strip():
            raise JUnitReportError("JUnit testcase is missing a non-empty name")

        classname = testcase.attrib.get(
            "classname",
            "unknown",
        )

        suite = testcase.attrib.get(
            "class",
            classname,
        )

        duration_ms = JUnitResultReader._duration_ms(testcase)

        return TestResult(
            test_id=f"{classname}::{name}",
            status=JUnitResultReader._status_of(testcase),
            duration_ms=duration_ms,
            suite=suite,
        )

    @staticmethod
    def _duration_ms(
        testcase: ElementTree.Element,
    ) -> int:
        raw_duration = testcase.attrib.get("time", "0")

        try:
            seconds = float(raw_duration)
        except ValueError as exc:
            raise JUnitReportError(f"Invalid testcase duration: {raw_duration!r}") from exc

        if seconds < 0:
            raise JUnitReportError("JUnit testcase duration must not be negative")

        return round(seconds * 1000)

    @staticmethod
    def _status_of(
        testcase: ElementTree.Element,
    ) -> TestStatus:
        if testcase.find("failure") is not None:
            return TestStatus.FAILED

        if testcase.find("error") is not None:
            return TestStatus.FAILED

        if testcase.find("skipped") is not None:
            return TestStatus.SKIPPED

        return TestStatus.PASSED
