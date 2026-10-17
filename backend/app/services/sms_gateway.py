"""
SMS Gateway Integration Service
Dispatches plain-language cellular notifications to smallholder farmer feature phones.
Supports Africa's Talking, Twilio, and an asynchronous Mock provider.
"""

import logging
from typing import Dict, Any
import httpx
from ..core.config import settings

logger = logging.getLogger(__name__)


class SMSGateway:
    @classmethod
    async def send_sms(cls, recipient_phone: str, message_body: str) -> Dict[str, Any]:
        """
        Dispatches SMS via configured provider.
        """
        provider = settings.SMS_PROVIDER.lower().strip()

        if provider == "africastalking" and settings.AFRICASTALKING_API_KEY:
            return await cls._send_africastalking(recipient_phone, message_body)
        elif provider == "twilio" and settings.TWILIO_AUTH_TOKEN:
            return await cls._send_twilio(recipient_phone, message_body)
        else:
            return await cls._send_mock(recipient_phone, message_body)

    @classmethod
    async def _send_mock(cls, phone: str, message: str) -> Dict[str, Any]:
        logger.info(f"[SMS MOCK GATEWAY] Dispatched to: {phone} | Text: '{message}'")
        return {
            "success": True,
            "provider": "mock",
            "recipient": phone,
            "message_id": f"mock-{int(hash(message) % 1000000)}"
        }

    @classmethod
    async def _send_africastalking(cls, phone: str, message: str) -> Dict[str, Any]:
        url = "https://api.africastalking.com/version1/messaging"
        headers = {
            "ApiKey": settings.AFRICASTALKING_API_KEY,
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "username": settings.AFRICASTALKING_USERNAME,
            "to": phone,
            "message": message,
            "from": settings.AFRICASTALKING_SENDER_ID
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, headers=headers, data=data)
                return {
                    "success": res.status_code in [200, 201],
                    "provider": "africastalking",
                    "status_code": res.status_code,
                    "response": res.json()
                }
        except Exception as e:
            logger.error(f"Africa's Talking SMS failed: {e}")
            return {"success": False, "provider": "africastalking", "error": str(e)}

    @classmethod
    async def _send_twilio(cls, phone: str, message: str) -> Dict[str, Any]:
        url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.TWILIO_ACCOUNT_SID}/Messages.json"
        auth = (settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        data = {
            "From": settings.TWILIO_FROM_NUMBER,
            "To": phone,
            "Body": message
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, auth=auth, data=data)
                return {
                    "success": res.status_code in [200, 201],
                    "provider": "twilio",
                    "status_code": res.status_code,
                    "response": res.json()
                }
        except Exception as e:
            logger.error(f"Twilio SMS failed: {e}")
            return {"success": False, "provider": "twilio", "error": str(e)}
