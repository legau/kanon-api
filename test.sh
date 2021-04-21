docker kill dock
docker run -p 8000:8000 --init -d --name dock --rm 09de0e096d25
curl --fail --retry 10 "localhost:8000/radices/float_sexa/?value=5"
