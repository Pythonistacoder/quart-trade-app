from quart import Blueprint, Response, redirect, request

from constants.global_contexts import kite_context
from constants.kite_credentials import API_SECRET

# from services.fetch_stocks import fetch_given_stocks

login = Blueprint("login", __name__)

@login.get("/login")
async def login_process()->Response:
    """
        This route is redirect to the login page of kite connect.
    """
    return redirect(location=kite_context.login_url())

@login.get("/home")
async def cdsl_access():
    """
        Route is defined in the kite trade which is hit when login is successful.

        Later it redirects to the authorization page of CDSL, where all stocks are
        authorized for buy or sell for that day.
    """

    data = kite_context.generate_session(
        request_token=request.args["request_token"],
        api_secret=API_SECRET
    )
    access_token = data["access_token"]
    kite_context.set_access_token(access_token=access_token)
    return {"message":"session started"}

