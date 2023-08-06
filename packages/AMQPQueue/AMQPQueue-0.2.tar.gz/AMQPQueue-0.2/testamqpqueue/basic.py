import threading
import logging

from amqpqueue import Producer, Consumer

FORMAT_CONS = '%(asctime)s %(name)-12s %(levelname)8s\t%(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT_CONS)

qp = Producer('test_q', addr='registry.ouls.ox.ac.uk:5672', userid='userid', password='password')
qp.put('test')
qc = Consumer('test_q', addr='registry.ouls.ox.ac.uk:5672', userid='userid', password='password')
print qc.get()
qc.task_done()

print "Starting thread that will in 5 seconds time, add a message on the queue"
threading.Timer(5.0, lambda: qp.put('{msg body}') ).start()
print "Trying to .get() - this is blocking and won't return unless a message has been posted"
print qc.get()
qc.task_done()
qc.delete(); qc.close()
qp.delete(); qp.close()

print "Done"
