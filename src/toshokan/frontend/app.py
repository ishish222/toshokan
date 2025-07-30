import gradio as gr
import os
import httpx
import uvicorn
from fastapi import FastAPI, Response, Request, status
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())
import logging

# libs that rely on env variables
from toshokan.frontend.middleware.auth import AuthMiddleware

# Load apps
from toshokan.frontend.dashboard import dashboard

# Load env variables
ENVIRONMENT = os.environ['ENVIRONMENT']
APP_HOST = os.environ['APP_HOST']
APP_PORT = os.environ['APP_PORT']
COGNITO_DOMAIN = os.environ['COGNITO_DOMAIN']
CLIENT_ID = os.environ['COGNITO_DOMAIN_CLIENT_ID']
REDIRECT_URI_LOGIN = os.environ['COGNITO_DOMAIN_REDIRECT_URI_LOGIN']
REDIRECT_URI_LOGOUT = os.environ['COGNITO_DOMAIN_REDIRECT_URI_LOGOUT']

### Session management
app = FastAPI()


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/login")
async def login():
    # Redirect user to Cognito login page
    return RedirectResponse(url=f'{COGNITO_DOMAIN}/login?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI_LOGIN}&scope=email+openid+profile')


@app.get("/login_done")
async def auth_callback(code: str, response: Response):
    # Exchange code for tokens
    token_url = f"{COGNITO_DOMAIN}/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI_LOGIN,
        "code": code,
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, headers=headers, data=data)
        tokens = response.json()

        # Here, we can issue your own authentication token or use Cognito's ID token
        # For simplicity, we return Cognito's ID token to the user

    # Set the ID token in a secure, HttpOnly cookie
    id_token_cookie = tokens.get("id_token")
    access_token_cookie = tokens.get("access_token")
    refresh_token_cookie = tokens.get("refresh_token")
    # Create a response object to set the cookie
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    # set relevant cookies
    response.set_cookie(
        key="id_token",
        value=id_token_cookie,
        httponly=True,
        secure=True,
        max_age=3600,  # Token expires in 1 hour
        samesite='Lax')

    response.set_cookie(
        key="access_token",
        value=access_token_cookie,
        httponly=True,
        secure=True,
        max_age=3600,  # Token expires in 1 hour
        samesite='Lax')

    response.set_cookie(
        key="refresh_token",
        value=refresh_token_cookie,
        httponly=True,
        secure=True,
        max_age=2592000,  # Token expires in 30 days
        samesite='Lax'
    )

    # Redirect or respond indicating successful authentication
    return response


@app.get("/refresh_tokens")
async def refresh_tokens(request: Request, response: Response):
    refresh_token = request.cookies.get("refresh_token")

    response_session_close = RedirectResponse(url="/login")
    response_session_close.delete_cookie(key="id_token")
    response_session_close.delete_cookie(key="access_token")
    response_session_close.delete_cookie(key="refresh_token")

    if not refresh_token:
        logging.error("No refresh token found")
        return response_session_close

    token_url = f"{COGNITO_DOMAIN}/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID,
        "refresh_token": refresh_token,
    }

    async with httpx.AsyncClient() as client:
        token_response = await client.post(token_url, headers=headers, data=data)

        if token_response.status_code != 200:
            return response_session_close

        tokens = token_response.json()

        id_token = tokens.get("id_token")
        access_token = tokens.get("access_token")

        # Set refreshed cookies
        response.set_cookie(
            key="id_token",
            value=id_token,
            httponly=True,
            secure=True,
            max_age=3600,  # Token expires in 1 hour
            samesite='Lax')

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            max_age=3600,  # Token expires in 1 hour
            samesite='Lax')

        return {"status": "tokens_refreshed"}


@app.get("/logout")
async def logout(response: Response):
    # Redirect to Cognito's logout URL
    cog_logout_url = f"{COGNITO_DOMAIN}/logout?client_id={CLIENT_ID}&response_type=code&logout_uri={REDIRECT_URI_LOGOUT}&redirect_uri={REDIRECT_URI_LOGOUT}&scope=email+openid+profile"
    return RedirectResponse(url=cog_logout_url)


@app.get("/logout_done")
async def logout_done():
    response_session_close = RedirectResponse(url="/login")
    response_session_close.delete_cookie(key="id_token")
    response_session_close.delete_cookie(key="access_token")
    response_session_close.delete_cookie(key="refresh_token")

    return response_session_close


@app.get("/")
def go_to_dashboard():
    return RedirectResponse("/dashboard")


@app.get("/dashboard/favicon.ico", include_in_schema=False)
async def dashboard_favicon():
    return FileResponse("static/favicon.ico")


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/favicon.ico")


if __name__ == '__main__':
    app.add_middleware(AuthMiddleware)
    gr.mount_gradio_app(app, dashboard, path='/dashboard', favicon_path='/dashboard/favicon.ico', allowed_paths=['/dashboard/output'])

    if ENVIRONMENT == 'local':
        LOCAL_CERT_PATH = os.environ['LOCAL_CERT_PATH']
        uvicorn.run(
            app,
            host=APP_HOST,
            port=int(APP_PORT),
            ssl_keyfile=f'{LOCAL_CERT_PATH}/server.key',
            ssl_certfile=f'{LOCAL_CERT_PATH}/server.crt',
            )
    else:
        uvicorn.run(
            app,
            host=APP_HOST,
            port=int(APP_PORT),
            )
