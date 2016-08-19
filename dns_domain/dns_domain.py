#!/usr/bin/env python

import argparse
import csv
import json
import zmq


def main(zmq_host, zmq_topic, port):

    # setup the zmq pub socket
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://*:{0}".format(port))

    # setup the zmq sub socket
    scontext = zmq.Context()
    ssocket = scontext.socket(zmq.SUB)
    ssocket.connect(zmq_host)
    ssocket.setsockopt(zmq.SUBSCRIBE, zmq_topic)

    running = True

    try:
        while running:
            msg = ssocket.recv()
            topic, data = msg.split(" ", 1)
            data = json.loads(data)

            # check if this is a query for a new domain
            query = data["Query"].split(".")
            domain = ".".join(query[-2:])
            subdomain = ".".join(query[:-2])
            data["Domain"] = domain
            data["Subdomain"] = subdomain

            print data

            # repackage data and deploy
            socket.send(zmq_topic + " " + json.dumps(data))

    except Exception as e:
        print e

if __name__ == "__main__":

    parser = argparse.ArgumentParser("Script to analyze incoming DNS traffic")
    parser.add_argument("-zh", "--zmq-host", default="tcp://localhost:7777", help="host running zmq dns stream, default tcp://localhost:7777")
    parser.add_argument("-zt", "--zmq-topic", default="dns", help="zmq topic to listen for")
    parser.add_argument("-p", "--port", default=9999, type=int,
        help="port to bind, default 9999")

    args = parser.parse_args()

    main(args.zmq_host, args.zmq_topic, args.port)
