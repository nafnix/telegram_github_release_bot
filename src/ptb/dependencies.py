import hashlib
import hmac
from typing import Annotated

import orjson
from fastapi import Body, Depends, Header

from src.config import settings
from src.exceptions import ForbiddenError


def valid_release_event(
    payload_body: dict = Body(),
    event: str = Header(alias='x-github-event'),
    signature_header: str = Header(alias='x-hub-signature-256'),
):
    """Verify that the payload was sent from GitHub by validating SHA256.

    Raise and return 403 if not authorized.

    Args:
        payload_body: original request body to verify (request.body())
        signature_header: header received from GitHub (x-hub-signature-256)
    """

    if not signature_header:
        raise ForbiddenError(message='x-hub-signature-256 header is missing!')

    hash_object = hmac.new(
        settings.GITHUB_WEBHOOK_SECRET.encode('utf-8'),
        msg=orjson.dumps(payload_body),
        digestmod=hashlib.sha256,
    )
    expected_signature = 'sha256=' + hash_object.hexdigest()
    if not hmac.compare_digest(expected_signature, signature_header):
        raise ForbiddenError(message="Request signatures didn't match!")

    if event == 'release' and (
        settings.GITHUB_WEBHOOK_EVENT is None
        or payload_body.get('action') in settings.GITHUB_WEBHOOK_EVENT
    ):
        return payload_body
    return None


ReleaseData = Annotated[dict | None, Depends(valid_release_event)]
