import logging
import os
from typing import Annotated

import pymongo
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel, BeforeValidator, EmailStr, Field, HttpUrl, field_serializer
from pydantic_core import Url

logger = logging.getLogger(__name__)

load_dotenv('.env')

PyObjectId = Annotated[str, BeforeValidator(str)]


class EmailSubscription(BaseModel):
    """A subscription to the newsletter."""

    id: PyObjectId | None = Field(alias='_id', default=None)
    email: EmailStr = Field(..., description='The email address of the subscriber')
    name: str = Field(..., description='The name of the subscriber')
    origin_url: HttpUrl | str = Field(..., description='The origin URL of the subscriber')

    @field_serializer('origin_url')
    def serialize_origin_url(self, val):
        if isinstance(val, Url):
            return str(val)
        return val


app = FastAPI(title='Newsletter API', version='0.1.0')
client = pymongo.MongoClient(os.environ['MONGODB_URL'])
db = client.newsletter
subscriber_collection = db.get_collection('subscribers')


@app.get('/')
def read_root():
    """Return a greeting."""
    return {'Hello': 'World'}


@app.post(
    '/subscribed/',
    response_description='New subscriber',
    response_model=EmailSubscription,
    status_code=201,
    response_model_by_alias=False,
)
def create_subscriber(subscriber: EmailSubscription):
    """Subscribe to the newsletter."""
    payload = subscriber.model_dump(by_alias=True, exclude=['id'])
    new_subscriber = subscriber_collection.insert_one(payload)
    created_subscriber = subscriber_collection.find_one({'_id': new_subscriber.inserted_id})

    logger.info('New subscriber: %s', created_subscriber)
    return created_subscriber
