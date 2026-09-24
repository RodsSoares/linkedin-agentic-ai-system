from app.schemas.argument import (
    Perspective,
    PerspectiveSet,
    SelectedPerspective,
)


def select_perspective(
    perspective_set: PerspectiveSet,
    perspective_id: str,
    human_guidance: str | None = None,
) -> SelectedPerspective:
    """
    Resolve an explicit human perspective selection.

    The runtime does not rank, infer, or recommend a perspective.
    The human-provided perspective_id is resolved deterministically
    against the available PerspectiveSet.
    """

    normalized_id = perspective_id.strip()

    if not normalized_id:
        raise ValueError(
            "perspective_id must not be empty."
        )

    perspective = _find_perspective(
        perspective_set=perspective_set,
        perspective_id=normalized_id,
    )

    normalized_guidance = _normalize_human_guidance(
        human_guidance
    )

    return SelectedPerspective(
        perspective=perspective,
        human_guidance=normalized_guidance,
    )


def _find_perspective(
    perspective_set: PerspectiveSet,
    perspective_id: str,
) -> Perspective:
    matches = [
        perspective
        for perspective in perspective_set.perspectives
        if perspective.perspective_id == perspective_id
    ]

    if not matches:
        raise ValueError(
            f"Perspective not found: {perspective_id}."
        )

    if len(matches) > 1:
        raise ValueError(
            f"Perspective id is not unique: {perspective_id}."
        )

    return matches[0]


def _normalize_human_guidance(
    human_guidance: str | None,
) -> str | None:
    if human_guidance is None:
        return None

    normalized_guidance = human_guidance.strip()

    return normalized_guidance or None