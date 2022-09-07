from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel
import requests
import models
import crud
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from schemas import transactionBase


class CallbackTr(BaseModel):
    id: str
    message: str
    status_code: str
    airtel_money_id: str


class Callback(BaseModel):
    transaction: CallbackTr


app = FastAPI()
models.Base.metadata.create_all(bind=engine)

# Dependency


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/transactions/", tags=['Transactions'])
def get_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    transactions = crud.get_transactions(db, skip=skip, limit=limit)
    print(len(transactions))
    if len(transactions) < 1:
        return {"message": "No transactions available"}
    return transactions


@app.post("/init-payment", tags=['Transactions'])
def init_payment(payment: transactionBase, db: Session = Depends(get_db)):
    if payment.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount must be greater than 0",
        )
    if not (payment.phone.startswith("72") or payment.phone.startswith("73")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number must start with either 73 or 72",
        )
    if not (len(payment.phone) == 9):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number must be 9 characters",
        )
    starter_transaction = crud.create_transaction(db, payment)

    # Requesting authorization token

    headers = {"Content-Type": "application/json", "Accept": "*/*"}
    body = {
        "client_id": "fe787496-0893-408f-b735-ef19537f6582",
        "client_secret": "*****************************",
        "grant_type": "client_credentials",
    }

    auth_res = requests.post(
        "https://openapiuat.airtel.africa/auth/oauth2/token", headers=headers, data=body
    )
    print(auth_res.json())

    if auth_res.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="something went wrong"
        )

    # Initiating payment request
    headers = {
        "Content-Type": "application/json",
        "Accept": "*/*",
        "X-Country": "RW",
        "X-Currency": "RWF",
        "Authorization": f"Bearer {auth_res.json().get('access_token')}",
    }

    body = {
        "reference": "Testing transaction",
        "subscriber": {"country": "RW", "currency": "RWF", "msisdn": payment.phone},
        "transaction": {
            "amount": payment.amount,
            "country": "RW",
            "currency": "RWF",
            "id": starter_transaction.id,
        },
    }

    r = requests.post(
        "https://openapiuat.airtel.africa/merchant/v1/payments/",
        headers=headers,
        data=body,
    )

    print(r.json())

    if r.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=r.get("status").get("message"),
        )

    starter_transaction = crud.create_transaction(db, payment)

    return {
        "status": "success",
        "transaction": starter_transaction,
        "message": "Please check your phone to confirm transaction if no prompt, please dial *182*7*1#",
    }


@app.post("/payment-callback", tags=['Transactions'])
def payment_callback(request: Callback):
    # Requesting authorization token
    headers = {"Content-Type": "application/json", "Accept": "*/*"}
    body = {
        "client_id": "fe787496-0893-408f-b735-ef19537f6582",
        "client_secret": "*****************************",
        "grant_type": "client_credentials",
    }

    auth_res = requests.post(
        "https://openapiuat.airtel.africa/auth/oauth2/token", headers=headers, data=body
    )
    print(auth_res.json())

    if auth_res.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="something went wrong"
        )

    # Initiating verification
    headers = {
        "Content-Type": "application/json",
        "Accept": "*/*",
        "X-Country": "RW",
        "X-Currency": "RWF",
        "Authorization": f"Bearer {auth_res.json().get('access_token')}",
    }

    transaction_enq_res = requests.get(
        "https://openapiuat.airtel.africa/standard/v1/payments/{id}".format(
            id=request.transaction.id
        ),
        headers=headers,
    )

    if transaction_enq_res != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=transaction_enq_res.get("status").get("message"),
        )
    # Update local transaction status

    return request
