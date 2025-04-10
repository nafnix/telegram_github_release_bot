from typing import cast

from fastapi import APIRouter, Request
from telegram import Update

from src.ptb import tgbot
from src.ptb.models import WebhookUpdate
from src.utils.telegram import text as tg_text

from .dependencies import ReleaseData


webhooks = APIRouter(tags=['PTB Webhooks'])


@webhooks.post('/telegram', response_model=None)
async def telegram(request: Request):
    """Handle incoming Telegram updates by putting them into the
    `update_queue`"""

    await tgbot.update_queue.put(
        Update.de_json(data=await request.json(), bot=tgbot.bot)
    )


@webhooks.get('/healthcheck', response_model=str)
async def health() -> str:
    """For the health endpoint, reply with a simple plain text message."""

    return 'The bot is still running fine :)'


@webhooks.post('/gh')
async def github_webhook_release(req: Request, data: ReleaseData):
    if data is None:
        return

    release: dict = data.pop('release')
    release_url = cast(str, release.get('html_url'))
    release_version = release.get('name')
    release_published_at = release.get('published_at')
    release_body = cast(str, release.get('body'))

    repository: dict = data.pop('repository')
    repo_name = repository.get('name')
    repo_url = cast(str, repository.get('html_url'))

    assets = []
    for asset in release.get('assets') or []:
        asset_name = asset.get('name')
        asset_url = asset.get('browser_download_url')
        assets.append({'name': asset_name, 'url': asset_url})

    assets_text = '\n'.join(
        tg_text.link(tg_text.escape(i['name']), i['url']) for i in assets
    )
    content = (
        f'🎉 Release New Version{tg_text.escape("!")} 🤓☝️\n'
        f'💥 Version: {tg_text.inline_code(tg_text.escape(release_version))}\n'
        f'🔗 Release URL: {tg_text.link(tg_text.escape(release_url), release_url)}\n'
        f'⏲️ Published At: {tg_text.inline_code(tg_text.escape(release_published_at))}\n'
        f'📦 Repository: {tg_text.inline_code(tg_text.escape(repo_name))}\n'
        f'🔗 Repository URL: {tg_text.link(tg_text.escape(repo_url), repo_url)}\n\n'
        f'📄 Files: \n{assets_text}\n\n'
        # f'{tg_text.escape(release_body)}'
    )

    await tgbot.update_queue.put(WebhookUpdate(text=content))
