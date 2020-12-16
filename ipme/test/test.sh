#!/bin/bash
curl -X POST http://localhost:5001/ip \
    --header "Content-Type: application/json" \
    --data '{"ip": "1.2.3.4"}'  

# wrong
curl -X POST http://localhost:5001/ip \
    --header "Content-Type: application/json" \
    --data '{"ip": "woof"}'  

curl -X POST http://localhost:5001/ip \
    --header "Content-Type: application/json" \
    --data '{"badkey": "woof"}'  

curl -X GET http://localhost:5001/