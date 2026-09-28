import httpx
import pytest

from fintables.api.endpoints.analyst_ratings import get_analyst_ratings
from fintables.models.analyst_rating import RatingType
from tests.conftest import load_fixture


@pytest.mark.asyncio
async def test_get_analyst_ratings(create_mock_client):
    data = load_fixture("analyst_ratings_asels.json")

    async def handler(request: httpx.Request) -> httpx.Response:
        assert "/analyst-ratings/" in str(request.url)
        assert request.url.params.get("code") == "ASELS"
        return httpx.Response(200, json=data)

    client = create_mock_client(handler)
    ratings = await get_analyst_ratings(client, "ASELS")

    assert len(ratings.results) == 4
    first = ratings.results[0]
    assert first.code == "ASELS"
    assert first.brokerage.code == "PHC"
    assert first.price_target == 546.6
    assert first.type == RatingType.ENDEKS_USTU
    assert first.in_model_portfolio is False

    second = ratings.results[1]
    assert second.type == RatingType.AL
    assert second.in_model_portfolio is True

    fourth = ratings.results[3]
    assert fourth.type is None
    assert fourth.price_target is None


@pytest.mark.asyncio
async def test_get_analyst_ratings_params(create_mock_client):
    captured_params = None

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_params
        captured_params = dict(request.url.params)
        return httpx.Response(200, json={"results": []})

    client = create_mock_client(handler)
    await get_analyst_ratings(client, "ASELS", brokerage_id="PHC", in_model_portfolio=True)

    assert captured_params["code"] == "ASELS"
    assert captured_params["brokerage_id"] == "PHC"
    assert captured_params["in_model_portfolio"] == "true"
