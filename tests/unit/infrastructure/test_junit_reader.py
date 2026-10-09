from pathlib import Path

from testops.domain.models import TestStatus as Status
from testops.infrastructure.junit_reader import JUnitResultReader


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
