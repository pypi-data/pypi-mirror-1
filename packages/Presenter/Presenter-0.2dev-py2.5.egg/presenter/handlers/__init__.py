"""
Package for file handlers for presenter.
"""

from collections import defaultdict

FILE_HANDLERS = []

try:
    from presenter.handlers.evince_handler import EvinceFileHandler
except ImportError:
    pass
else:
    FILE_HANDLERS.append(EvinceFileHandler)

try:
    from presenter.handlers.video_handler import VideoFileHandler
except ImportError:
    pass
else:
    FILE_HANDLERS.append(VideoFileHandler)

MIME_HANDLERS = defaultdict(list)
for handler in FILE_HANDLERS:
    for mime in handler.mime_types:
        MIME_HANDLERS[mime].append(handler)

