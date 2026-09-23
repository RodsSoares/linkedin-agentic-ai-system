from pydantic import ValidationError

from app.schemas.post import PostCandidate


def test_post_candidate_valid():
    post = PostCandidate(
        post_id="123",
        author_name="Nandan",
        post_text="Post sobre agentes de IA.",
        post_url="https://linkedin.com/posts/123",
    )

    assert post.post_id == "123"
    assert post.source == "linkedin"


def test_post_candidate_without_required_text():
    try:
        PostCandidate(
            post_id="123",
            author_name="Nandan",
            post_text=None,
            post_url="https://linkedin.com/posts/123",
        )
    except ValidationError:
        assert True
    else:
        assert False