from pydantic import BaseModel, Field, model_validator


class DiscoveryMeasurement(BaseModel):
    """
    Deterministic measurement contract for one bounded discovery run.

    The discovery funnel is intentionally separated from semantic judgment.

    Funnel:

    queries
    ↓
    discovered results
    ↓
    novel results
    ↓
    readable results
    ↓
    normalized PostCandidates
    ↓
    opportunity evaluations
    ↓
    HIGH / MEDIUM / LOW

    Counts represent factual execution state and therefore belong to Python,
    not to the LLM.
    """

    query_count: int = Field(default=0, ge=0)

    discovered_count: int = Field(default=0, ge=0)
    novel_count: int = Field(default=0, ge=0)
    readable_count: int = Field(default=0, ge=0)
    normalized_count: int = Field(default=0, ge=0)

    opportunity_evaluated_count: int = Field(default=0, ge=0)

    high_opportunity_count: int = Field(default=0, ge=0)
    medium_opportunity_count: int = Field(default=0, ge=0)
    low_opportunity_count: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def validate_discovery_funnel(self) -> "DiscoveryMeasurement":
        if self.novel_count > self.discovered_count:
            raise ValueError(
                "novel_count cannot exceed discovered_count."
            )

        if self.readable_count > self.novel_count:
            raise ValueError(
                "readable_count cannot exceed novel_count."
            )

        if self.normalized_count > self.readable_count:
            raise ValueError(
                "normalized_count cannot exceed readable_count."
            )

        if self.opportunity_evaluated_count > self.normalized_count:
            raise ValueError(
                "opportunity_evaluated_count cannot exceed normalized_count."
            )

        classified_count = (
            self.high_opportunity_count
            + self.medium_opportunity_count
            + self.low_opportunity_count
        )

        if classified_count != self.opportunity_evaluated_count:
            raise ValueError(
                "HIGH + MEDIUM + LOW opportunity counts must equal "
                "opportunity_evaluated_count."
            )

        return self

    @property
    def duplicate_or_known_count(self) -> int:
        return self.discovered_count - self.novel_count

    @property
    def unreadable_count(self) -> int:
        return self.novel_count - self.readable_count

    @property
    def normalization_failure_count(self) -> int:
        return self.readable_count - self.normalized_count

    @property
    def coverage_rate(self) -> float:
        """
        Fraction of discovered search results that are novel.

        This measures whether discovery is expanding beyond already-known
        content rather than repeatedly finding the same URLs.
        """
        return self._safe_ratio(
            self.novel_count,
            self.discovered_count,
        )

    @property
    def readability_rate(self) -> float:
        """
        Fraction of novel URLs that can actually be read by the bounded reader.
        """
        return self._safe_ratio(
            self.readable_count,
            self.novel_count,
        )

    @property
    def normalization_rate(self) -> float:
        """
        Fraction of readable results successfully converted into PostCandidate.
        """
        return self._safe_ratio(
            self.normalized_count,
            self.readable_count,
        )

    @property
    def opportunity_yield(self) -> float:
        """
        Fraction of evaluated candidates classified as MEDIUM or HIGH.

        LOW candidates are valid discoveries, but they do not represent
        useful professional interaction opportunities under the current
        Opportunity policy.
        """
        valuable_count = (
            self.high_opportunity_count
            + self.medium_opportunity_count
        )

        return self._safe_ratio(
            valuable_count,
            self.opportunity_evaluated_count,
        )

    @property
    def high_opportunity_yield(self) -> float:
        """
        Fraction of evaluated candidates classified as HIGH.
        """
        return self._safe_ratio(
            self.high_opportunity_count,
            self.opportunity_evaluated_count,
        )

    @staticmethod
    def _safe_ratio(
        numerator: int,
        denominator: int,
    ) -> float:
        if denominator == 0:
            return 0.0

        return round(
            numerator / denominator,
            4,
        )
    