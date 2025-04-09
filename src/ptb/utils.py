from telegram.ext import Application, CallbackContext, ExtBot

from src.config import settings
from src.ptb.models import WebhookUpdate


class CustomContext(CallbackContext[ExtBot, dict, dict, dict]):
    """
    Custom CallbackContext class that makes `user_data` available for updates
    of type `WebhookUpdate`.
    """

    @classmethod
    def from_update(
        cls,
        update: object,
        telegram_bot: Application,
    ) -> 'CustomContext':
        if isinstance(update, WebhookUpdate):
            return cls(
                application=telegram_bot,
                user_id=settings.TELEGRAM_ADMIN_CHAT_ID,
            )
        return super().from_update(update, telegram_bot)
