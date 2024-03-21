from fastapi import APIRouter

from src.ptb.webhooks import webhooks as ptb_webhooks


router = APIRouter()
router.include_router(ptb_webhooks, prefix='/webhooks/ptb')
