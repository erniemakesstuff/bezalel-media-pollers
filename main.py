import multiprocessing
import logging
import health_service
import consumer

logger = logging.getLogger(__name__)

print("starting server and consumers")
app = health_service.app # Flask run initializes server.
serviceListener = multiprocessing.Process(target=app.run(port=8080, debug=True, host='0.0.0.0'))
processConsumer = multiprocessing.Process(target=consumer.start_poll)
processConsumer.start() # Async pollers in background; no need to wait/join. Infinite.
serviceListener.start()
print("services started")
