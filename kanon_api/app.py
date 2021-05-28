from concurrent.futures.process import ProcessPoolExecutor

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import calculations, calendars, ephemerides

app = FastAPI()

app.include_router(calendars.router)
app.include_router(ephemerides.router)
app.include_router(calculations.router)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup():
    app.state.executor = ProcessPoolExecutor()


@app.on_event("shutdown")
async def on_shutdown():
    app.state.executor.shutdown()


@app.get("/health")
def health_check():
    return "OK"
