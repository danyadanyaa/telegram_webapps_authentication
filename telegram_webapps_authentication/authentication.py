import base64
import hashlib
import hmac
import json
import time
from typing import Any, Dict
from urllib.parse import unquote
from pydantic import BaseModel
from urllib.parse import parse_qs

class TelegramUser(BaseModel):
    """
    Represents a Telegram user.
    """
    id: int
    first_name: str
    last_name: str
    username: str
    language_code: str

class InitialData(BaseModel):
    """
    Represents the initial data received from Telegram.
    """
    query_id: str
    user: TelegramUser
    auth_date: str
    hash: str


class Authenticator:
    """
    Handles authentication and validation of initial data from Telegram.
    """
    REQUIRED_KEYS: set = {'query_id', 'user', 'auth_date', 'hash'}
    USER_DATA_KEYS: list = ['id', 'username', 'first_name', 'last_name', 'language_code']

    def __init__(self, bot_token: str):
        """
        Initializes the Authenticator with a bot token.

        Args:
            bot_token (str): Token for the Telegram bot.
        """
        self.bot_token = bot_token
        self.secret_key = hmac.new("WebAppData".encode(), bot_token.encode(), hashlib.sha256).digest()

    def initial_data_parse(self, init_data: str) -> Dict[str, Any]:
        """
        Parses the initial data from a query string format into a dictionary.

        Args:
            init_data (str): Initial data in query string format.

        Returns:
            Dict[str, Any]: Parsed data as a dictionary.

        Raises:
            ValueError: If any required keys are missing in the data.
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

    def extract_user_data(self, init_data: str) -> Dict[str, str]:
        """
        Extracts user-specific data from the initial data.

        Args:
            init_data (str): Initial data in query string format.

        Returns:
            Dict[str, str]: Extracted user data.

        Raises:
            ValueError: If 'user' key is missing in initial data or if user data is not valid JSON.
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

    def validate_init_data(self, init_data: str, check_time = False) -> bool:
        """
        Validates the initial data by comparing the provided hash with the computed hash.

        Args:
            init_data (str): Initial data in query string format.

        Returns:
            bool: True if the data is valid, False otherwise.

        Raises:
            ValueError: If 'hash' key is not found in `init_data`.
        """
        parsed_data = {key: unquote(value[0]) for key, value in parse_qs(init_data).items()}

        received_hash = parsed_data.pop('hash', None)
        auth_date = int(parsed_data.get('auth_date', 0))

        if not received_hash or not auth_date:
            return False
        
        current_time = int(time.time())

        # Hash timed out․
        if check_time:
            if current_time - auth_date > 300 :  
                return False
        
        data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(parsed_data.items()))

        computed_hash = hmac.new(
            key=self.secret_key,
            msg=data_check_string.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()

        return computed_hash == received_hash

    def get_telegram_user(self, init_data: str) -> TelegramUser:
        """
        Extracts and returns a `TelegramUser` object from the initial data.

        Args:
            init_data (str): Initial data in query string format.

        Returns:
            TelegramUser: Extracted Telegram user information.

        Raises:
            ValueError: If `init_data` is not valid.
        """
        if not self.validate_init_data(init_data):
            raise ValueError("init_data is not valid")

        user_data = self.extract_user_data(init_data)

        return TelegramUser(**user_data)

    def get_initial_data(self, init_data: str) -> InitialData:
        """
        Extracts and returns an `InitialData` object from the initial data.

        Args:
            init_data (str): Initial data in query string format.

        Returns:
            InitialData: Extracted initial data information.

        Raises:
            ValueError: If `init_data` is not valid.
        """
        if not self.validate_init_data(init_data):
            raise ValueError("init_data is not valid")

        init_data_dict = self.initial_data_parse(init_data)

        user = self.get_telegram_user(init_data)
        return InitialData(query_id=init_data_dict['query_id'], user=user, auth_date=init_data_dict['auth_date'], hash=init_data_dict['hash'])

    def encode_init_data(self, data: str) -> str:
        """
        Encodes initial data to base64 format.

        Args:
            data (str): Data to be encoded.

        Returns:
            str: Base64 encoded data.
        """
        return base64.b64encode(data.encode()).decode()

    def decode_init_data(self, encoded_data: str) -> str:
        """
        Decodes initial data from base64 format.

        Args:
            encoded_data (str): Base64 encoded data.

        Returns:
            str: Decoded data.
        """
        return base64.b64decode(encoded_data.encode()).decode()