# multi-agent-crew-ai

## Overview

#### Agents
- Every Agent has certain role to play

#### Tasks
- Every task is executed by an agent to complete jobs for their defined role


## Developer setup
- Follow : https://docs.crewai.com/installation

#### Using UV as installer
- Instead of using standard pip for installation, crew ai suggests to use UV as the downloader tool
- Install UD : `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Install crew ai libraries using uv : `uv tool install crewai`


#### Create a new project (one time)
`crewai create flow test_flow`

#### Before running crew, run the following to download all the dependencies and create a virtual environment
`crewai install`

#### If any dependencies not installed use
`uv add <package-name>`

## Run this project
`crewai run`


## Reference 
- Learnt from Deeplearning AI
- Official documentation - https://docs.crewai.com/installation 
