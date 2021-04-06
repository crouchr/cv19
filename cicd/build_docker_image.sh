#!/bin/bash
cd ..
docker build --no-cache -t cicd:cvd19 .
docker tag cicd:cvd19 registry:5000/cvd19:$VERSION
docker push registry:5000/cvd19:$VERSION
docker rmi cicd:cvd19
