from datetime import datetime, timedelta
from fastapi import FastAPI
import threading
import uvicorn
import asyncio
import signal
import time

from model import core
from model.database import engine, SessionLocal, get_db
from model.core import Timestamp
from routers.timestamps import router as timestamps_router

core.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(router=timestamps_router)

exit_flag = threading.Event()


def record_timestamp():
    while not exit_flag.is_set():
        db = SessionLocal()
        new_timestamp = Timestamp()
        db.add(new_timestamp)
        db.commit()
        db.close()
        time.sleep(5)


def delete_old_timestamps():
    while not exit_flag.is_set():
        db = SessionLocal()
        one_minute_ago = datetime.utcnow() - timedelta(minutes=1)
        db.query(Timestamp).filter(Timestamp.timestamp < one_minute_ago).delete()
        db.commit()
        db.close()
        time.sleep(10)


@app.on_event("startup")
def startup_event():
    get_db()
    global t1, t2
    t1 = threading.Thread(target=record_timestamp)
    t2 = threading.Thread(target=delete_old_timestamps)

    t1.start()
    t2.start()


# Processing signal CTRL + C
async def handle(sig, frame):
    print("Сигнал получен, завершаем потоки")
    exit_flag.set()
    # close the streams
    t1.join()
    t2.join()
    print("Выключаем сервер FASTAPI")
    await server.shutdown()

# Set signal to complete Ctrl + C
signal.signal(signal.SIGINT, lambda sig, frame: asyncio.create_task(handle(sig, frame)))

if __name__ == "__main__":
    uvicorn_config = uvicorn.Config(app, host="127.0.0.1", port=8000)
    server = uvicorn.Server(uvicorn_config)
    server.run()
