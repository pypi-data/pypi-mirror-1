import logging

logger = logging.getLogger('clue.bzrserver')
logger.setLevel(level=logging.INFO)

security_logger = logging.getLogger('clue.bzrserver.security')
security_logger.setLevel(level=logging.WARNING)
