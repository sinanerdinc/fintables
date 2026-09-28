from fintables.api.client import FintablesClient
from fintables.models.post import PostDetail, PostPage


async def list_posts(
    client: FintablesClient,
    main_category: str = "bist",
    page: int | None = None,
) -> PostPage:
    """Yazıları listeler."""
    params: dict[str, str | int] = {"main_category": main_category}
    if page is not None:
        params["page"] = page

    response = await client.get(
        "/posts/",
        params=params,
        requires_auth=True,
    )
    return PostPage.model_validate(response.json())


async def get_post(
    client: FintablesClient,
    slug: str,
) -> PostDetail:
    """Yazı detayını (içeriğiyle birlikte) getirir."""
    response = await client.get(
        f"/posts/{slug}/",
        requires_auth=True,
    )
    return PostDetail.model_validate(response.json())
