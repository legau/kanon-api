from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import calendars, ephemerides, radices

app = FastAPI()

app.include_router(calendars.router)
app.include_router(ephemerides.router)
app.include_router(radices.router)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return "OK"
