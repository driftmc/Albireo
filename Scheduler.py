import platform
if platform.system() == 'Linux':
    from twisted.internet import epollreactor
    epollreactor.install()
else:
    from twisted.internet import selectreactor
    selectreactor.install()

from twisted.internet import reactor, threads


from feed.FeedFromDMHY import FeedFromDMHY
from yaml import load
from utils.SessionManager import SessionManager
from domain.Episode import Episode
from domain.Bangumi import Bangumi
from twisted.internet.task import LoopingCall
from utils.DownloadManager import download_manager
from utils.exceptions import SchedulerError
import os, errno
import logging

logger = logging.getLogger()

isDebug = os.getenv('DEBUG', False)

if isDebug:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

FORMAT = '%(asctime)-15s %(message)s'

logging.basicConfig(format=FORMAT)

class Scheduler:

    def __init__(self):
        fr = open('./config/config.yml', 'r')
        config = load(fr)
        self.interval = int(config['task']['interval']) * 60
        self.base_path = config['download']['location']
        try:
            if not os.path.exists(self.base_path):
                os.makedirs(self.base_path)
                logger.info('create base dir %s successfully', self.base_path)
        except OSError as exception:
            if exception.errno == errno.EACCES:
                # permission denied
                raise exception
            else:
                logger.error(exception)

    def start(self):
        lc = LoopingCall(self.scan_bangumi)
        lc.start(self.interval)

    def _scan_bangumi_in_thread(self):
        logger.info('start scan bangumi')

        session = SessionManager.Session

        result = session.query(Bangumi).\
            filter(Bangumi.status == Bangumi.STATUS_ON_AIR)
        try:
            for bangumi in result:
                episode_result = session.query(Episode).\
                    filter(Episode.bangumi==bangumi).\
                    filter(Episode.status==Episode.STATUS_NOT_DOWNLOADED)

                task = FeedFromDMHY(bangumi, episode_result, self.base_path)
                task_result = task.parse_feed()
                if task_result is None:
                    session.commit()
                    logger.info('scan finished')
                else:
                    logger.warn('scan finished with exception')
                    logger.warn(task_result)


        except OSError as os_error:
            logger.error(os_error)
        except Exception as error:
            logger.error(error)

    def scan_bangumi(self):
        threads.deferToThread(self._scan_bangumi_in_thread)


scheduler = Scheduler()

def on_connected(result):
    # logger.info(result)
    scheduler.start()

def on_connect_fail(result):
    logger.error(result)
    reactor.stop()

d = download_manager.connect()
d.addCallback(on_connected)
d.addErrback(on_connect_fail)

reactor.run()