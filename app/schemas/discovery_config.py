from pydantic import BaseModel, Field, field_validator, model_validator


class DiscoverySearchStrategy(BaseModel):
    name: str = Field(min_length=1)
    enabled: bool = True
    template: str = Field(min_length=1)

    @field_validator("name", "template")
    @classmethod
    def validate_non_blank_text(cls, value: str) -> str:
        normalized = value.strip()

        if not normalized:
            raise ValueError("Value cannot be blank.")

        return normalized

    @field_validator("template")
    @classmethod
    def validate_topic_placeholder(cls, value: str) -> str:
        if "{topic}" not in value:
            raise ValueError(
                "Discovery search strategy template must contain "
                "the '{topic}' placeholder."
            )

        return value


class DiscoverySearchConfig(BaseModel):
    max_results_per_query: int = Field(default=5, ge=1, le=20)
    topics: list[str] = Field(min_length=1)
    strategies: list[DiscoverySearchStrategy] = Field(min_length=1)

    @field_validator("topics")
    @classmethod
    def validate_topics(cls, topics: list[str]) -> list[str]:
        normalized_topics: list[str] = []
        seen: set[str] = set()

        for topic in topics:
            normalized = topic.strip()

            if not normalized:
                raise ValueError("Discovery topics cannot contain blank values.")

            normalized_key = normalized.casefold()

            if normalized_key in seen:
                raise ValueError(
                    f"Duplicate discovery topic: {normalized}"
                )

            seen.add(normalized_key)
            normalized_topics.append(normalized)

        return normalized_topics

    @model_validator(mode="after")
    def validate_enabled_strategy_exists(self):
        if not any(strategy.enabled for strategy in self.strategies):
            raise ValueError(
                "At least one discovery search strategy must be enabled."
            )

        strategy_names = [
            strategy.name.casefold()
            for strategy in self.strategies
        ]

        if len(strategy_names) != len(set(strategy_names)):
            raise ValueError(
                "Discovery search strategy names must be unique."
            )

        return self


class DiscoveryLimitsConfig(BaseModel):
    max_queries: int = Field(default=5, ge=1, le=50)
    max_candidates: int = Field(default=10, ge=1, le=100)
    max_opportunity_evaluations: int = Field(
        default=5,
        ge=1,
        le=100,
    )


class DiscoveryConfig(BaseModel):
    version: int = Field(default=1, ge=1)
    search: DiscoverySearchConfig
    discovery: DiscoveryLimitsConfig

    @model_validator(mode="after")
    def validate_query_capacity(self):
        enabled_strategy_count = sum(
            1
            for strategy in self.search.strategies
            if strategy.enabled
        )

        available_query_count = (
            len(self.search.topics) * enabled_strategy_count
        )

        if self.discovery.max_queries > available_query_count:
            raise ValueError(
                "discovery.max_queries cannot exceed the number of "
                "queries available from enabled strategies and topics."
            )

        return self
    