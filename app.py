from uvicorn import run as uvicorn_run

from kami.main import create_app
from kami.database import db, MODELS
from kami.config import DEBUG, JWT_SECRET


app = create_app()


@app.on_event("startup")
def database_connect():
    if db.is_closed():
        db.connect()

    db.create_tables(MODELS)

@app.on_event("shutdown")
def database_disconnect():
    if not db.is_closed():
        db.disconnect()


def main() -> None:
    if str(JWT_SECRET) == "secret":
        print("WARN: Please generate a JWT Secret.")

    uvicorn_run(
        "app:app",
        host="0.0.0.0",
        port=8765,
        reload=DEBUG
    )


if __name__ == "__main__":
    main()
