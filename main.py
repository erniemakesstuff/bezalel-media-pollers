import multiprocessing
import logging
import health_service
import consumer

logger = logging.getLogger(__name__)

logger.info("starting server and consumers")
app = health_service.app # Flask run initializes server.
# TODO: Update this to NOT expose all interaces; remove 0.0...
serviceListener = multiprocessing.Process(target=app.run(port=8080, debug=True))
processConsumer = multiprocessing.Process(target=consumer.start_poll)
processConsumer.start() # Async pollers in background; no need to wait/join. Infinite.
serviceListener.start()
logger.info("services started")
processConsumer.join()
serviceListener.join()
