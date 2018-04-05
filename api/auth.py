import cryptography.hazmat.backends.openssl.rsa
import jwt
import json
import requests

from jwt import DecodeError, ExpiredSignatureError
from functools import lru_cache 

def checktoken(access_token) -> dict:
  try: 
    decoded_token = decode_token(access_token, 'https://api.d10l.de')
  except (DecodeError, ExpiredSignatureError):
      return None
  decoded_token['uid'] = decoded_token['sub']
  return decoded_token




def decode_token(token: str, oauth_client_id: str):
    token_signing_key_id = _get_token_signing_key_id(token)
    keys = _get_public_keys()
    # TODO if the key ID is not in the set we should return 401?
    token_key = keys[token_signing_key_id]
    # verifying the ID token is an important part of securing the OAuth flow with Google
    # https://developers.google.com/identity/sign-in/web/backend-auth
    return jwt.decode(
        token,
        key=token_key,
        audience=oauth_client_id)


def _get_token_signing_key_id(token: str) -> str:
    # This isn't ideal, but I can either use that or reimplement and test it, which doesn't make
    # sense either. It'd be good to submit a pull request upstream that would expose that as
    # a public function.
    # https://github.com/jpadilla/pyjwt/issues/292
    parse_token_output = jwt.PyJWS()._load(token)  # pylint: disable=protected-access
    # the outputs are payload, signing_input, header, signature
    token_header = parse_token_output[2]
    return token_header['kid']

@lru_cache(maxsize=1)
def _get_public_keys() -> dict:
    """Gets the set of JWKs (https://tools.ietf.org/html/rfc7517#section-5) provided by Auth0.

    These keys will change, but they live for longer than 24 hours, so one hour of caching (which
    this function does), should be OK.

    Returns:
        Mapping of key ID's ("kid" fields) to RSA public keys usable by PyJWT.
    """
    public_keys_url = 'https://d10l.eu.auth0.com/.well-known/jwks.json'
    r = requests.get(public_keys_url)
    r.raise_for_status()
    jwk_set = r.json()
    public_keys = {}
    for key_dict in jwk_set['keys']:
        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key_dict))
        public_keys[key_dict['kid']] = public_key
    return public_keys