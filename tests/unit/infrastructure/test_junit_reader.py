from pathlib import Path

import pytest

from testops.domain.models import TestStatus as Status
from testops.infrastructure.junit_reader import JUnitReportError, JUnitResultReader


def test_reads_junit_results(tmp_path: Path) -> None:
    report = tmp_path / "junit.xml"

    report.write_text(
        """
        <testsuite name="checkout">
            <testcase
                classname="checkout.payment"
                name="test_successful_payment"
                time="0.82"
            />

            <testcase
                classname="checkout.payment"
                name="test_declined_card"
                time="0.41"
            >
                <failure message="Expected 200"/>
            </testcase>

            <testcase
                classname="checkout.payment"
                name="test_pending_feature"
                time="0.01"
            >
                <skipped/>
            </testcase>
        </testsuite>
        """,
        encoding="utf-8",
    )

    results = JUnitResultReader(report).read()

    assert len(results) == 3

    assert results[0].test_id == ("checkout.payment::test_successful_payment")
    assert results[0].status is Status.PASSED
    assert results[0].duration_ms == 820
    assert results[0].suite == "checkout.payment"

    assert results[1].status is Status.FAILED
    assert results[1].duration_ms == 410

    assert results[2].status is Status.SKIPPED
    assert results[2].duration_ms == 10


def test_reads_junit_defaults_and_error_status(tmp_path: Path) -> None:
    report = tmp_path / "junit.xml"
    report.write_text(
        '<testsuite><testcase name="test_error"><error/></testcase></testsuite>',
        encoding="utf-8",
    )

    result = JUnitResultReader(report).read()[0]

    assert result.test_id == "unknown::test_error"
    assert result.status is Status.FAILED
    assert result.duration_ms == 0
    assert result.suite == "unknown"


@pytest.mark.parametrize(
    ("xml", "message"),
    [
        ("<testsuite><testcase/></testsuite>", "missing a non-empty name"),
        (
            '<testsuite><testcase name="test" time="invalid"/></testsuite>',
            "Invalid testcase duration",
        ),
        ('<testsuite><testcase name="test" time="-1"/></testsuite>', "must not be negative"),
    ],
)
def test_rejects_invalid_testcases(tmp_path: Path, xml: str, message: str) -> None:
    report = tmp_path / "junit.xml"
    report.write_text(xml, encoding="utf-8")

    with pytest.raises(JUnitReportError, match=message):
        JUnitResultReader(report).read()


def test_rejects_unreadable_and_malformed_reports(tmp_path: Path) -> None:
    with pytest.raises(JUnitReportError, match="Unable to read JUnit report"):
        JUnitResultReader(tmp_path / "missing.xml").read()

    malformed = tmp_path / "malformed.xml"
    malformed.write_text("<testsuite>", encoding="utf-8")

    with pytest.raises(JUnitReportError, match="Unable to read JUnit report"):
        JUnitResultReader(malformed).read()
