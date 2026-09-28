import logging

from fintables.api.client import FintablesClient
from fintables.models.search import (
    SearchDocument,
    SearchGroup,
    SearchHit,
    SearchResponse,
)

_logger = logging.getLogger("fintables.search")

SEARCH_PAYLOAD = {
    "searches": [
        {
            "collection": "symbols",
            "filter_by": "type:equity",
            "per_page": 5,
            "query_by": "code,title,tags",
            "query_by_weights": "2,1,1",
            "text_match_type": "max_weight",
        },
        {
            "collection": "symbols",
            "filter_by": "type:future",
            "per_page": 5,
            "query_by": "code,title,tags",
            "query_by_weights": "2,1,1",
            "text_match_type": "max_weight",
        },
        {
            "collection": "symbols",
            "filter_by": "type:warrant",
            "per_page": 5,
            "query_by": "code,title,tags",
            "query_by_weights": "2,1,1",
            "sort_by": "_text_match:desc,priority:desc",
            "text_match_type": "max_weight",
        },
        {
            "collection": "symbols",
            "filter_by": "type:!=equity && type:!=future && type:!=warrant",
            "per_page": 5,
            "query_by": "code,title,tags",
            "query_by_weights": "2,1,1",
            "text_match_type": "max_weight",
        },
    ]
}


async def search(client: FintablesClient, query: str) -> SearchResponse:
    """Performs search. Uses Typesense gate if key configured, otherwise public mobile search."""
    if client.settings.typesense_api_key:
        try:
            response = await client.post(
                "/search/multi_search",
                params={"q": query},
                json=SEARCH_PAYLOAD,
                is_gate=True,
            )
            return SearchResponse.model_validate(response.json())
        except Exception as e:
            _logger.debug("Gate search failed, falling back to mobile: %s", type(e).__name__)

    # Public mobile search fallback (api.fintables.com)
    try:
        response = await client.get("/mobile/search/", params={"q": query})
        data = response.json()
        groups = []
        for item in data.get("results", []):
            cat_title = item.get("title", "Sonuçlar")
            symbols = item.get("symbols", [])
            hits = [
                SearchHit(
                    document=SearchDocument(
                        code=s.get("code", ""),
                        id=s.get("code", ""),
                        title=s.get("title", ""),
                        type=s.get("type", "equity"),
                        flags=s.get("flags") or [],
                    ),
                    text_match=100,
                )
                for s in symbols
            ]
            groups.append(
                SearchGroup(
                    title=cat_title,
                    found=len(symbols),
                    hits=hits,
                    out_of=len(symbols),
                    page=1,
                )
            )
        return SearchResponse(results=groups)
    except Exception as e:
        _logger.debug("Mobile search failed, falling back to gate: %s", type(e).__name__)

    response = await client.post(
        "/search/multi_search",
        params={"q": query},
        json=SEARCH_PAYLOAD,
        is_gate=True,
    )
    return SearchResponse.model_validate(response.json())
