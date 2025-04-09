from pydantic import BaseModel


class WebhookUpdate(BaseModel):
    """Simple dataclass to wrap a custom update type"""

    text: str
    assets: list[str] | None = None
