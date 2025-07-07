from dotenv import load_dotenv

from fastapi import FastAPI

from .api import router

load_dotenv()

app = FastAPI(title="TailorTalk API")
app.include_router(router)
