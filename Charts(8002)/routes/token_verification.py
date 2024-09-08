import time
from jose import jwk, jwt
from jose.utils import base64url_decode
import json
import urllib.request
from fastapi import Header
from fastapi import WebSocket,HTTPException, status


region = 'ap-south-1'
userpool_id = 'ap-south-1_YEH0sqfmB'
app_client_id = '4nql0ttol3en0nir4d56ctdc6i'
keys_url = 'https://cognito-idp.{}.amazonaws.com/{}/.well-known/jwks.json'.format(region, userpool_id)

with urllib.request.urlopen(keys_url) as f:
    response = f.read()
keys = json.loads(response.decode('utf-8'))['keys']


def verifyToken(event):
    token = event['token']
    
    # Verify the token structure
    if token.count('.') != 2:
        # print('Invalid token structure')
        return False
    
    # get the kid from the headers prior to verification
    try:
        headers = jwt.get_unverified_headers(token)
    except jwt.JWTError as e:
        # print(f"Error decoding token headers: {e}")
        return False

    kid = headers['kid']
    # search for the kid in the downloaded public keys
    key_index = -1
    for i in range(len(keys)):
        if kid == keys[i]['kid']:
            key_index = i
            break
    if key_index == -1:
        # print('Public key not found in jwks.json')
        return False

    # construct the public key
    public_key = jwk.construct(keys[key_index])

    # get the last two sections of the token,
    # message and signature (encoded in base64)
    message, encoded_signature = str(token).rsplit('.', 1)
    # decode the signature
    decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))
    # verify the signature
    if not public_key.verify(message.encode("utf8"), decoded_signature):
        # print('Signature verification failed')
        return False
    # print('Signature successfully verified')
    # since we passed the verification, we can now safely
    # use the unverified claims
    claims = jwt.get_unverified_claims(token)
    # additionally we can verify the token expiration
    if time.time() > claims['exp']:
        # print('Token is expired')
        return False
    # and the Audience  (use claims['client_id'] if verifying an access token)
    if claims['aud'] != app_client_id:
        # print('Token was not issued for this audience')
        return False
    return claims


async def get_websocket_user(websocket: WebSocket):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
    claims = verifyToken({"token": token})
    if not claims:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    return claims["email"]


def get_current_user(authorization: str = Header(...)):
    try:
        token = authorization.split(" ")[1]  # Assuming the token is sent as "Bearer <token>"
        claims = verifyToken({"token": token})
        if not claims:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return claims["email"]
    except IndexError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is malformed",
            headers={"WWW-Authenticate": "Bearer"},
        )
