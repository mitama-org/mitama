from mitama.auth import AuthorizationError, check_jwt
from mitama.http import get_session

async def get_login_state(request):
    sess = await get_session(request)
    if 'jwt_token' in sess:
        user = check_jwt(sess['jwt_token'])
    else:
        raise AuthorizationError('Unauthorized')
