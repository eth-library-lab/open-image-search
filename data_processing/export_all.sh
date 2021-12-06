#!/bin/bash
source ./.env.dev
export $(cut -d= -f1 ./.env.dev)