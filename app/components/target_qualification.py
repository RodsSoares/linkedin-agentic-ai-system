from urllib.parse import urlparse

from app.schemas.target_qualification import TargetQualification


LINKEDIN_HOSTS = {
    "linkedin.com",
    "www.linkedin.com",
}


def qualify_target(url: str) -> TargetQualification:
    """
    Deterministically classify a discovered URL before semantic
    opportunity evaluation.

    Classification and policy are intentionally separated:
    this function describes what the target appears to be and whether
    it is currently eligible as an interaction target.
    """

    normalized_url = url.strip()

    if not normalized_url:
        return TargetQualification(
            target_type="UNKNOWN",
            is_interaction_target=False,
            reason="URL is empty.",
        )

    try:
        parsed = urlparse(normalized_url)
    except ValueError:
        return TargetQualification(
            target_type="UNKNOWN",
            is_interaction_target=False,
            reason="URL could not be parsed.",
        )

    host = (parsed.hostname or "").lower()
    path = parsed.path.rstrip("/").lower()

    if host not in LINKEDIN_HOSTS:
        return TargetQualification(
            target_type="EXTERNAL_CONTENT",
            is_interaction_target=False,
            reason="Target is outside LinkedIn.",
        )

    if path.startswith("/posts/"):
        return TargetQualification(
            target_type="INTERACTION_TARGET",
            is_interaction_target=True,
            reason="LinkedIn public post permalink.",
        )

    if path.startswith("/feed/update/"):
        return TargetQualification(
            target_type="INTERACTION_TARGET",
            is_interaction_target=True,
            reason="LinkedIn feed update permalink.",
        )

    if path.startswith("/pulse/"):
        return TargetQualification(
            target_type="LINKEDIN_CONTENT",
            is_interaction_target=False,
            reason="LinkedIn article or Pulse content.",
        )

    if path.startswith("/top-content/"):
        return TargetQualification(
            target_type="LINKEDIN_CONTENT",
            is_interaction_target=False,
            reason="LinkedIn aggregated editorial content.",
        )

    if path.startswith("/company/"):
        return TargetQualification(
            target_type="LINKEDIN_NON_INTERACTION",
            is_interaction_target=False,
            reason="LinkedIn company page.",
        )

    if path.startswith("/learning/"):
        return TargetQualification(
            target_type="LINKEDIN_NON_INTERACTION",
            is_interaction_target=False,
            reason="LinkedIn Learning content.",
        )

    return TargetQualification(
        target_type="UNKNOWN",
        is_interaction_target=False,
        reason="LinkedIn URL type is not yet recognized.",
    )
