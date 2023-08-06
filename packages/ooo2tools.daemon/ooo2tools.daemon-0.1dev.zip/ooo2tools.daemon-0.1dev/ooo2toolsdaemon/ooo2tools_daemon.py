import sys, time, os, re, commands, logging
from daemon import Daemon
from os import listdir, removedirs
from tempfile import mkstemp
 
SHARED_DIR = '/home/alegros/dev/share'
OUT_LOG = '/home/alegros/dev/out.log'
CMD_EXE = 'python /home/alegros/dev/ressources/footer.py --sequence='

logging.basicConfig(filename=OUT_LOG,level=logging.DEBUG,)
logger = logging.getLogger('Daemon')

class MyDaemon(Daemon):
    def run(self):
        logger.info('premiere boucle!')
        while True:
            if listdir(SHARED_DIR):
                files = [(SHARED_DIR + '/' + item) for item in listdir(SHARED_DIR)]
                todo_dirs = [item for item in files if os.path.isdir(item)]
                ready = []
                status = ''
                output = ''
                for item in todo_dirs:
                    if item + '.lock' not in files\
                        and item + '.processed' not in files:
                        ready.append(item)
                if ready:
                    logger.info('ready : ' + str(ready))
                    """
                    d is a dictionnary containing the item (files) in 'ready'
                    as values, and their last modification time as their
                    keys, so that d.get(min(d)) return the most ancient file
                    """
                    d = dict(zip([os.stat(item)[8] for item in ready], ready))
                    first_task = d.get(min(d))
                    logger.info('first task : ' + str(first_task))
                    task = first_task + '/seq.txt'
                    cmd = CMD_EXE + task
                    logger.info('cmd : ' + cmd)
                    status, output = commands.getstatusoutput(cmd)
                    logger.info('status : ' + str(status) + '\n')
                    if status == 0:
                        f = open(first_task + '.processed', 'w')
                        f.close()
            time.sleep(1)


if __name__ == "__main__":
    daemon = MyDaemon('/tmp/daemon-example.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)
