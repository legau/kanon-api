from fastapi import FastAPI

from .routes import calendars, ephemerides, radices

app = FastAPI()

app.include_router(calendars.router)
app.include_router(ephemerides.router)
app.include_router(radices.router)


@app.get("/health")
def health_check():
    return "OK"
