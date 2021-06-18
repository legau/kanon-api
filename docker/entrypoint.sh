#!/bin/bash
uvicorn --host $HOST --port $PORT kanon_api.app:app
