from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Personalization,Email
from dotenv import load_dotenv


# Load env variables
load_dotenv()

app = FastAPI()

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL")


# Request Model
class EmailRequest(BaseModel):
    subject: str
    body: str
    to: List[EmailStr]


def send_email_sendgrid(request: EmailRequest):
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)

        mail = Mail(
            from_email=FROM_EMAIL,
            subject=request.subject,
            html_content=request.body
        )

        personalization = Personalization()

        for email in request.to:
            personalization.add_to(Email(email))

        mail.add_personalization(personalization)

        response = sg.send(mail)

        return response.status_code

    except Exception as e:
        raise Exception(str(e))


@app.get("/")
def home():
    return {"message": "Email API is running"}


@app.post("/send-email")
def send_email(request: EmailRequest):
    try:
        status = send_email_sendgrid(request)

        return {
            "status": "success",
            "sendgrid_status": status,
            "message": f"Sent to {len(request.to)} email(s)"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))