# Documentation

## Data Models

### `TelegramUser`

Represents a Telegram user.

- **Attributes:**
  - `id` (int): User ID.
  - `first_name` (str): User's first name.
  - `last_name` (str): User's last name.
  - `username` (str): User's username.
  - `language_code` (str): User's language code.

### `InitialData`

Represents the initial data received from Telegram.

- **Attributes:**
  - `query_id` (str): Unique query ID.
  - `user` (`TelegramUser`): User information.
  - `auth_date` (str): Authentication date.
  - `hash` (str): Hash for data validation.

## `Authenticator` Class

The `Authenticator` class provides methods for handling and validating the initial data from Telegram.

### `__init__(self, bot_token: str)`

Initializes the `Authenticator` with a bot token.

- **Args:**
  - `bot_token` (str): Token for the Telegram bot.

### `initial_data_parse(self, init_data: str) -> Dict[str, Any]`

Parses the initial data from a query string format into a dictionary.

- **Args:**
  - `init_data` (str): Initial data in query string format.
- **Returns:**
  - `Dict[str, Any]`: Parsed data as a dictionary.
- **Raises:**
  - `ValueError`: If any required keys are missing in the data.

### `initial_data_prepare(self, init_data_dict: Dict[str, Any]) -> str`

Prepares the cleaned data string by excluding the 'hash' key and sorting the remaining key-value pairs.

- **Args:**
  - `init_data_dict` (Dict[str, Any]): Dictionary of initial data.
- **Returns:**
  - `str`: Prepared data string.
- **Raises:**
  - `ValueError`: If `init_data_dict` is empty or if no data is available after excluding the 'hash' key.
  - `TypeError`: If any value is not a string.

### `extract_user_data(self, init_data: str) -> Dict[str, str]`

Extracts user-specific data from the initial data.

- **Args:**
  - `init_data` (str): Initial data in query string format.
- **Returns:**
  - `Dict[str, str]`: Extracted user data.
- **Raises:**
  - `ValueError`: If 'user' key is missing in initial data or if user data is not valid JSON.

### `validate_init_data(self, init_data: str) -> bool`

Validates the initial data by comparing the provided hash with the computed hash.

- **Args:**
  - `init_data` (str): Initial data in query string format.
- **Returns:**
  - `bool`: True if the data is valid, False otherwise.
- **Raises:**
  - `ValueError`: If 'hash' key is not found in `init_data`.

### `get_telegram_user(self, init_data: str) -> TelegramUser`

Extracts and returns a `TelegramUser` object from the initial data.

- **Args:**
  - `init_data` (str): Initial data in query string format.
- **Returns:**
  - `TelegramUser`: Extracted Telegram user information.
- **Raises:**
  - `ValueError`: If `init_data` is not valid.

### `get_initial_data(self, init_data: str) -> InitialData`

Extracts and returns an `InitialData` object from the initial data.

- **Args:**
  - `init_data` (str): Initial data in query string format.
- **Returns:**
  - `InitialData`: Extracted initial data information.
- **Raises:**
  - `ValueError`: If `init_data` is not valid.

### `encode_init_data(self, data: str) -> str`

Encodes initial data to base64 format.

- **Args:**
  - `data` (str): Data to be encoded.
- **Returns:**
  - `str`: Base64 encoded data.

### `decode_init_data(self, encoded_data: str) -> str`

Decodes initial data from base64 format.

- **Args:**
  - `encoded_data` (str): Base64 encoded data.
- **Returns:**
  - `str`: Decoded data.