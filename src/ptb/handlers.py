import html

from telegram import Update
from telegram.constants import ParseMode

from src.config import settings
from src.ptb.constants import WEBHOOK_URL
from src.ptb.models import WebhookUpdate
from src.ptb.utils import CustomContext
from src.utils.telegram import text


async def start(update: Update, context: CustomContext) -> None:
    """Display a message with instructions on how to use this bot."""
    payload_url = html.escape(
        f'{WEBHOOK_URL}/submitpayload?user_id=<your user id>&payload=<payload>'
    )
    text = (
        f'To check if the bot is still running, '
        f'call <code>{WEBHOOK_URL}/healthcheck</code>.\n\n'
        f'To post a custom update, call <code>{payload_url}</code>.'
    )

    assert update.message is not None
    assert update.effective_user is not None
    assert update.effective_chat is not None
    await update.message.reply_markdown_v2(
        f'your user id `{update.effective_user.id}`, '
        f'the chat id `{update.effective_chat.id}`'
    )
    await update.message.reply_html(text=text)


async def webhook_update(
    update: WebhookUpdate,
    context: CustomContext,
) -> None:
    """Handle custom updates."""

    # text = (
    #     f'The user {chat_member.user.mention_html()} has sent a new payload. '
    #     f'So far they have sent the following payloads: \n\n'
    #     f'• <code>{combined_payloads}</code>'
    # )
    await context.bot.send_message(
        chat_id=settings.TELEGRAM_ADMIN_CHAT_ID,
        text=text.escape(update.text),
        parse_mode=ParseMode.MARKDOWN_V2,
    )
