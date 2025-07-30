from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from gradio.context import LocalContext
import os
import jwt
import httpx
from datetime import datetime, timezone


ENVIRONMENT = os.environ['ENVIRONMENT']
APP_HOST = os.environ['APP_HOST']
APP_PORT = os.environ['APP_PORT']
COGNITO_DOMAIN = os.environ['COGNITO_DOMAIN']
CLIENT_ID = os.environ['COGNITO_DOMAIN_CLIENT_ID']
COGNITO_DOMAIN_REGION = os.environ['COGNITO_DOMAIN_REGION']
COGNITO_POOL_ID = os.environ['COGNITO_DOMAIN_USER_POOL_ID']
JWKS_URL = f"https://cognito-idp.{COGNITO_DOMAIN_REGION}.amazonaws.com/{COGNITO_POOL_ID}/.well-known/jwks.json"

oauth2_scheme = OAuth2AuthorizationCodeBearer(authorizationUrl=f"{COGNITO_DOMAIN}/login", tokenUrl=f"{COGNITO_DOMAIN}/oauth2/token")


async def get_current_user(
    id_token: str = Depends(oauth2_scheme),
    access_token: str = Depends(oauth2_scheme)
):
    # Verify the JWT token
    try:
        jwks_client = jwt.PyJWKClient(JWKS_URL)
        signing_key = jwks_client.get_signing_key_from_jwt(id_token)

        if signing_key:

            payload = jwt.decode(
                id_token,
                signing_key,
                algorithms=["RS256"],
                audience=CLIENT_ID,
                access_token=access_token
            )

            cognito_id = payload.get("sub")
            email = payload.get("email")

            if cognito_id is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Cognito ID not found in token.")
            if email is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not found in token.")

            return {"cognito_id": cognito_id, "email": email}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Could not validate credentials")


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # List of routes that don't require authentication
        open_routes = [
            "/login",
            "/login_done",
            "/logout_done",
            "/logout",
            "/health",
            "/favicon.ico",
            "/dashboard/favicon.ico"
            ]

        if request.url.path in open_routes:
            # Skip middleware and continue to the requested route
            return await call_next(request)

        response_session_close = RedirectResponse(url="/login")
        response_session_close.delete_cookie(key="id_token")
        response_session_close.delete_cookie(key="access_token")
        response_session_close.delete_cookie(key="refresh_token")

        try:
            # Perform the token validation logic here
            id_token = request.cookies.get("id_token")
            access_token = request.cookies.get("access_token")

            if not id_token or not access_token:
                return response_session_close

            # Decode token without verification to check expiration
            payload = jwt.decode(id_token, options={"verify_signature": False})
            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp, timezone.utc) <= datetime.now(timezone.utc):

                # Token has expired, attempt to refresh
                refresh_response = await httpx.AsyncClient().get(f"https://{APP_HOST}:{APP_PORT}/refresh_tokens")

                if refresh_response.status_code != 200:
                    # Refresh failed, redirect to login
                    return response_session_close

                if refresh_response.status_code == 200:
                    # Update tokens from the refreshed cookies
                    cookies = refresh_response.cookies
                    id_token = cookies.get("id_token")
                    access_token = cookies.get("access_token")
                else:
                    # Refresh failed, redirect to login
                    return response_session_close

            user = await get_current_user(id_token, access_token)

            session_info = user
            LocalContext.session_info = session_info

            response = await call_next(request)

            return response

        except Exception as e:
            print(f"HTTPException: {e}")
            return response_session_close
