import logging
import requests
from fastapi import APIRouter, Depends, HTTPException
from app.core.config import settings
from app.api.v1.dependencies.auth import get_current_user

router = APIRouter()
logger = logging.getLogger("app.api.powerbi")


@router.get("/embed-info", summary="Generate Power BI embed tokens")
async def get_embed_info(
    _current_user = Depends(get_current_user)
):
    """
    Fetches embed parameters and tokens for secure reporting layout insertion.
    Uses simulated bypass parameters if cloud credentials are not configured in settings.
    """
    tenant_id = settings.POWERBI_TENANT_ID
    client_id = settings.POWERBI_CLIENT_ID
    client_secret = settings.POWERBI_CLIENT_SECRET
    workspace_id = settings.POWERBI_WORKSPACE_ID
    report_id = settings.POWERBI_REPORT_ID

    # ── Dev/Bypass Mode (If credentials missing) ──
    if not all([tenant_id, client_id, client_secret, workspace_id, report_id]):
        logger.warning("Power BI credentials not configured. Returning simulated embed credentials.")
        return {
            "embedUrl": "https://app.powerbi.com/reportEmbed?reportId=simulated-report-id&groupId=simulated-group-id",
            "accessToken": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6Ik1vY2tUb2tlbiJ9.simulated.token",
            "reportId": "simulated-report-id",
            "expiry": "2099-12-31T23:59:59Z",
            "isSimulated": True
        }

    try:
        # 1. Fetch Azure Active Directory OAuth Access Token
        token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        token_data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "https://analysis.windows.net/powerbi/api/.default"
        }
        
        token_res = requests.post(token_url, data=token_data, timeout=10)
        token_res.raise_for_status()
        aad_token = token_res.json().get("access_token")

        # 2. Call Power BI REST API to Generate Embed Token
        embed_token_url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/reports/{report_id}/GenerateToken"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {aad_token}"
        }
        # Generate token with Read permissions
        payload = {"accessLevel": "View"}
        
        embed_res = requests.post(embed_token_url, json=payload, headers=headers, timeout=10)
        embed_res.raise_for_status()
        
        embed_token = embed_res.json().get("token")
        embed_url = f"https://app.powerbi.com/reportEmbed?reportId={report_id}&groupId={workspace_id}"

        return {
            "embedUrl": embed_url,
            "accessToken": embed_token,
            "reportId": report_id,
            "expiry": embed_res.json().get("expiration"),
            "isSimulated": False
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch credentials from Microsoft API: {e}")
        raise HTTPException(
            status_code=502,
            detail="Error connecting to Power BI OAuth / Token generator service."
        )
