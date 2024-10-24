from fastapi import FastAPI
from pydantic import BaseModel, HttpUrl


class EmailSubscription(BaseModel):
    email: str
    name: str
    origin: HttpUrl


app = FastAPI()


@app.get('/')
def read_root():
    return {'Hello': 'World'}


@app.post('/subscribe')
def subscribe(subscription: EmailSubscription):
    return {'message': 'Subscription received', 'email': subscription.email, 'name': subscription.name}
