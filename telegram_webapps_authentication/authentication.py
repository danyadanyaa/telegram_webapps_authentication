import base64
import hashlib
import hmac
import json
from typing import Any, Dict
from urllib.parse import unquote
from pydantic import BaseModel


class TelegramUser(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str
    language_code: str


class InitialData(BaseModel):
    query_id: str
    user: TelegramUser
    auth_date: str
    hash: str


class Authenticator:
    REQUIRED_KEYS: set = {'query_id', 'user', 'auth_date', 'hash'}
    USER_DATA_KEYS: list = ['id', 'username', 'first_name', 'last_name', 'language_code']

    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.secret_key = hmac.new("WebAppData".encode(), bot_token.encode(), hashlib.sha256).digest()

    def initial_data_parse(self, init_data: str) -> Dict[str, Any]:
        """
        Parse the initial data from a query string format into a dictionary.
        """
        parsed_data = {}
        for item in init_data.split('&'):
            if '=' in item:
                key, value = item.split('=', 1)
                if key in self.REQUIRED_KEYS:
                    parsed_data[key] = unquote(value)

        missing_keys = self.REQUIRED_KEYS - parsed_data.keys()
        if missing_keys:
            raise ValueError(f"Missing required keys: {', '.join(missing_keys)}")

        return parsed_data

    def initial_data_prepare(self, init_data_dict: Dict[str, Any]) -> str:
        """
        Prepare the cleaned data string by excluding 'hash' key and sorting the remaining key-value pairs.
        """
        if not init_data_dict:
            raise ValueError("init_data_dict cannot be empty")

        prepared_data = []
        for k, v in sorted(init_data_dict.items()):
            if k == 'hash':
                continue
            if v is None:
                raise ValueError(f"Value for key '{k}' is None")
            if not isinstance(v, str):
                raise TypeError(f"Value for key '{k}' must be a string, got {type(v).__name__}")
            prepared_data.append(f"{k}={v}")

        if not prepared_data:
            raise ValueError("No data to prepare after excluding 'hash' key")

        return '\n'.join(prepared_data)

    def extract_user_data(self, init_data: str) -> Dict[str, str]:
        """
        Extract user-specific data from the initial data.
        """
        init_data_dict = self.initial_data_parse(init_data)

        if 'user' not in init_data_dict:
            raise ValueError("Missing 'user' key in initial data")

        try:
            user_data = json.loads(init_data_dict['user'])
        except json.JSONDecodeError:
            raise ValueError("User data is not valid JSON")

        extracted_data = {k: user_data.get(k, '') for k in self.USER_DATA_KEYS}

        missing_keys = [k for k in self.USER_DATA_KEYS if k not in user_data]
        if missing_keys:
            raise ValueError(f"Missing user data keys: {', '.join(missing_keys)}")

        return extracted_data

    def validate_init_data(self, init_data: str) -> bool:
        """
        Validate the initial data by comparing the provided hash with the computed hash.
        """
        init_data_dict = self.initial_data_parse(init_data)
        if 'hash' not in init_data_dict:
            raise ValueError("Hash not found in init_data")

        init_data_cleaned = self.initial_data_prepare(init_data_dict)
        hash_token = hmac.new(self.secret_key, init_data_cleaned.encode(), hashlib.sha256)

        return hash_token.hexdigest() == init_data_dict['hash']

    def get_telegram_user(self, init_data: str) -> TelegramUser:
        """
        Extract and return a TelegramUser object from the initial data.
        """
        if not self.validate_init_data(init_data):
            raise ValueError("init_data is not valid")

        user_data = self.extract_user_data(init_data)

        return TelegramUser(**user_data)

    def get_initial_data(self, init_data: str) -> InitialData:
        """
        Extract and return an InitialData object from the initial data.
        """
        if not self.validate_init_data(init_data):
            raise ValueError("init_data is not valid")

        init_data_dict = self.initial_data_parse(init_data)

        user = self.get_telegram_user(init_data)
        return InitialData(query_id=init_data_dict['query_id'], user=user, auth_date=init_data_dict['auth_date'], hash=init_data_dict['hash'])

    def encode_init_data(self, data: str) -> str:
        """
        Encode initial data to base64 format.
        """
        return base64.b64encode(data.encode()).decode()

    def decode_init_data(self, encoded_data: str) -> str:
        """
        Decode initial data from base64 format.
        """
        return base64.b64decode(encoded_data.encode()).decode()
