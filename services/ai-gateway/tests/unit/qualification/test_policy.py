from app.realtime.qualification.policy import (
    MedicareQualificationPolicy,
)
from app.realtime.qualification.types import (
    LeadData,
)


def create_policy():
    return MedicareQualificationPolicy(min_age=65)


def test_incomplete_lead():
    result = create_policy().evaluate(LeadData(consent=True))

    assert result.complete is False
    assert result.qualified is None


def test_age_disqualification():
    result = create_policy().evaluate(
        LeadData(
            consent=True,
            age=64,
        )
    )

    assert result.complete is True
    assert result.qualified is False

    assert result.reason == "age_below_minimum"


def test_part_a_disqualification():
    result = create_policy().evaluate(
        LeadData(
            consent=True,
            age=70,
            medicare_part_a=False,
        )
    )

    assert result.complete is True
    assert result.qualified is False


def test_part_b_disqualification():
    result = create_policy().evaluate(
        LeadData(
            consent=True,
            age=70,
            medicare_part_a=True,
            medicare_part_b=False,
        )
    )

    assert result.complete is True
    assert result.qualified is False


def test_qualified():
    result = create_policy().evaluate(
        LeadData(
            consent=True,
            full_name="Daniel Smith",
            age=70,
            medicare_part_a=True,
            medicare_part_b=True,
            zip_code="75001",
        )
    )

    assert result.complete is True
    assert result.qualified is True
