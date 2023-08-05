import sys, os
from stellaris.service.serve import ServeStellaris
import stellaris

log = stellaris._logger

config_file = sys.argv[1]

server = ServeStellaris(config_file)

try:
    server.start()
except KeyboardInterrupt, e:
    log.debug("Received a keyboard interrupt, stopping server.")
    server.stop()
except SystemExit, e:
    log.debug("Received system exit, stopping server.")
    server.stop()


