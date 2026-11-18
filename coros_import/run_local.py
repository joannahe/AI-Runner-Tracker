"""Start the consent app on the loopback interface only."""

import uvicorn

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8767, app_dir=__file__.rsplit("/", 1)[0], log_level="warning", access_log=False)
