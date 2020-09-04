
from mitama.http import get_session

async def get_login_state(request):
    sess = await get_session(request)
    return check_jwt(sess['jwt_token'])

