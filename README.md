# Telegram Authentication Module

This module provides functionality for handling authentication and validation of initial data received from Telegram. It includes parsing, preparing, validating, and encoding/decoding initial data. It also provides data models for representing Telegram users and initial data.

## Installation

To use this module, you need to have Python 3.x installed. Install the necessary dependencies using pip:

```bash
pip install telegram_webapps_authentication
```
## Example

Here is an example of how to use the `Authenticator` class with FastAPI:

```python
from typing import Optional

from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel

from telegram_webapps_authentication import Authenticator, TelegramUser

app = FastAPI()

BOT_TOKEN = "YOUR_BOT_TOKEN"  # Replace it with your real telegram bot token
authenticator = Authenticator(BOT_TOKEN)

class Message(BaseModel):
    text: str

@app.get("/validate")
def validate_init_data(authorization: Optional[str] = Header()):
    try:
        if authenticator.validate_init_data(authorization):
            initial_data = authenticator.get_initial_data(authorization)
            return {"message": initial_data.dict()}
        else:
            raise HTTPException(status_code=400, detail="Data is not valid")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/get_user")
def get_user_instance(authorization: Optional[str] = Header()):
    user = authenticator.get_telegram_user(authorization)
    return user

@app.post("/message")
async def send_message(
    message: Message,
    user: TelegramUser = Depends(authenticator.get_telegram_user),
):
    """
    Your backend logic
    """
    ...
```

