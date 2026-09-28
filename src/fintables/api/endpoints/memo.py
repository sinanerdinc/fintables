from fintables.api.client import FintablesClient
from fintables.models.memo import Memo


async def list_memos(client: FintablesClient) -> list[Memo]:
    """Lists all memos for the authenticated user."""
    response = await client.get("/memos/", requires_auth=True)
    data = response.json()
    return [Memo.model_validate(item) for item in data]


async def create_memo(client: FintablesClient, code: str, content: str) -> Memo:
    """Creates a new memo for a symbol."""
    code_clean = code.strip().upper()
    response = await client.post(
        "/memos/",
        json={"code": code_clean, "content": content},
        requires_auth=True,
    )
    return Memo.model_validate(response.json())


async def update_memo(client: FintablesClient, memo_id: int, code: str, content: str) -> Memo:
    """Updates an existing memo."""
    code_clean = code.strip().upper()
    response = await client.put(
        f"/memos/{memo_id}/",
        json={"id": memo_id, "code": code_clean, "content": content},
        requires_auth=True,
    )
    return Memo.model_validate(response.json())


async def delete_memo(client: FintablesClient, memo_id: int) -> None:
    """Deletes a memo by ID."""
    await client.delete(f"/memos/{memo_id}/", requires_auth=True)
