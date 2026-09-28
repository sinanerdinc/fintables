from fintables.api.client import FintablesClient
from fintables.models.newsletter import NewsletterDetail, NewsletterPage


async def list_newsletters(
    client: FintablesClient,
    main_category: str = "bist",
    page_size: int = 100,
    page: int | None = None,
) -> NewsletterPage:
    """Bültenleri listeler."""
    params: dict[str, str | int] = {
        "main_category": main_category,
        "page_size": page_size,
    }
    if page is not None:
        params["page"] = page

    response = await client.get(
        "/newsletters/",
        params=params,
        requires_auth=True,
    )
    return NewsletterPage.model_validate(response.json())


async def get_newsletter(
    client: FintablesClient,
    slug: str,
) -> NewsletterDetail:
    """Bülten detayını (içeriğiyle birlikte) getirir."""
    response = await client.get(
        f"/newsletters/{slug}/",
        requires_auth=True,
    )
    return NewsletterDetail.model_validate(response.json())
