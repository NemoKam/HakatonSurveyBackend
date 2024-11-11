import uvicorn

import config

if __name__ == "__main__":
    uvicorn.run("fastapp.fast:app", host=config.PROJECT_HOST, port=config.PROJECT_PORT, workers=config.CELERY_WORKER_COUNT)