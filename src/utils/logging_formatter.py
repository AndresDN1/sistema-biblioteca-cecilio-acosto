import json
import logging
from datetime import datetime


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        logging_payload = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "module": record.module,
            "function": record.funcName,
            "line_number": record.lineno,
            "message": record.message,
        }

        if record.exc_info:
            logging_payload["exception"] = self.formatException(record.exc_info)

        extra_context = getattr(record, "extra_context", None)
        if extra_context and isinstance(extra_context, dict):
            logging_payload.update(extra_context)

        return json.dumps(logging_payload)
