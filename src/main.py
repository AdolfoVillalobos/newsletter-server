import logging
import os
from typing import Annotated

import pymongo
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, BeforeValidator, EmailStr, Field, HttpUrl, field_serializer
from pydantic_core import Url

logger = logging.getLogger('uvicorn')

load_dotenv('.env')

PyObjectId = Annotated[str, BeforeValidator(str)]


class EmailSubscription(BaseModel):
    """A subscription to the newsletter."""

    id: PyObjectId | None = Field(alias='_id', default=None)
    email: EmailStr = Field(..., description='The email address of the subscriber')
    name: str = Field(..., description='The name of the subscriber')
    domain: HttpUrl | str = Field(..., description='The origin URL of the subscriber')

    @field_serializer('domain')
    def serialize_domain(self, val):
        if isinstance(val, Url):
            return str(val)
        return val


app = FastAPI(title='Newsletter API', version='0.1.0', debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
    allow_credentials=True,
)

client = pymongo.MongoClient(os.environ['MONGODB_URL'])
db = client.newsletter
subscriber_collection = db.get_collection('subscribers')

logger.info('Connected to MongoDB')


@app.get('/')
def read_root():
    """Return a greeting."""
    return {'Hello': 'World'}


@app.post(
    '/subscribe/',
    response_description='New subscriber',
    response_model=EmailSubscription,
    status_code=201,
    response_model_by_alias=False,
)
def create_subscriber(subscriber: EmailSubscription):
    """Subscribe to the newsletter."""
    logger.info('Creating subscriber: %s', subscriber)
    payload = subscriber.model_dump(by_alias=True, exclude=['id'])
    new_subscriber = subscriber_collection.update_one(payload, {'$set': payload}, upsert=True)
    created_subscriber = subscriber_collection.find_one({'_id': new_subscriber.upserted_id})

    logger.info('New subscriber: %s', created_subscriber)
    return created_subscriber
