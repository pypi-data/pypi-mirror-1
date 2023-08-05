#!/usr/bin/env python

from httptestserver import StoppableHttpRequestHandler, start_server

start_server(10001, StoppableHttpRequestHandler)
