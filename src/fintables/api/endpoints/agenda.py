from typing import Literal

from fintables.api.client import FintablesClient
from fintables.models.agenda import AgendaItem

AgendaTime = Literal["today", "thisWeek", "nextWeek"]


async def get_agenda(
    client: FintablesClient,
    time: AgendaTime = "today",
) -> list[AgendaItem]:
    """Ajanda etkinliklerini getirir (bugün / bu hafta / gelecek hafta)."""
    response = await client.get(
        "/mobile/agenda/",
        params={"time": time},
        requires_auth=True,
    )
    data = response.json()
    if isinstance(data, list):
        return [AgendaItem.model_validate(item) for item in data]
    # API ileride sayfalı yanıt dönerse results listesini kullan
    return [AgendaItem.model_validate(item) for item in data.get("results", [])]
