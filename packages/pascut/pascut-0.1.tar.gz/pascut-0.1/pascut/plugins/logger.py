from pascut.plugin import LoggerPlugin
import sys
import logging

class Logger(LoggerPlugin):

    def __init__(self, *args, **kwargs):
        self.loggers = dict()
        self._verbose = kwargs['verbose']
        hdlr = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                '%Y-%m-%d %H:%M:%S')
        hdlr.setFormatter(formatter)
        self.handler = hdlr

    def get_logger(self, obj):
        if type(obj) is str:
            name = obj
        else:
            name = obj.__class__.__name__
        logger = None
        if name in self.loggers:
            logger = self.loggers[name]
        else:
            logger = logging.getLogger(name)
            logger.addHandler(self.handler)
            if self._verbose:
                logger.setLevel(logging.DEBUG)
            else:
                logger.setLevel(logging.INFO)

        return logger
    
    def on_debug(self, msg, obj):
        self.get_logger(obj).debug(msg)

    def on_info(self, msg, obj):
        self.get_logger(obj).info(msg)

