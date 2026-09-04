from app.schemas.writer import WriterInput


def writer(input_data: WriterInput) -> str:
    post = input_data.post

    if input_data.previous_draft is not None:
        return (
            f"REVISADO — Comentário candidato para o post de {post.author_name}: "
            f"{post.post_text}"
        )

    return (
        f"Comentário candidato para o post de {post.author_name}: "
        f"{post.post_text}"
    )