from fintables.api.client import FintablesClient
from fintables.models.video import VideoItem, VideoPage


async def list_videos(
    client: FintablesClient,
    type_: str = "video",
    main_category: str = "bist",
    page: int | None = None,
) -> VideoPage:
    """Videoları listeler."""
    params: dict[str, str | int] = {
        "type": type_,
        "main_category": main_category,
    }
    if page is not None:
        params["page"] = page

    response = await client.get(
        "/videos/",
        params=params,
    )
    return VideoPage.model_validate(response.json())


async def get_video(
    client: FintablesClient,
    slug: str,
) -> VideoItem:
    """Video detayını getirir."""
    response = await client.get(
        f"/videos/{slug}/",
    )
    return VideoItem.model_validate(response.json())
