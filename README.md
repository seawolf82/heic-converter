# heic-converter
A simple program written in python to convert from heic to jpg into a Docker  

To Build This Docker run:

docker build --no-cache -t heic-converter .

To run this Docker:

docker run --name heic-converter -p 5000:5000 heic-converter:latest
