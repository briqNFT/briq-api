import logging
import json
import datetime

class CustomLoggingFormatter(logging.Formatter):
    def __init__(self):
        super(CustomLoggingFormatter, self).__init__()

    def format(self, record: logging.LogRecord):
        record.message = record.getMessage()
        input_data = {
            "time": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "severity": record.levelname,
            "message": record.message,
            "name": record.name,
        }
        if record.exc_info:
            input_data['exc_info'] = self.formatException(record.exc_info)
        if record.stack_info:
            input_data['stack_info'] = self.formatStack(record.stack_info)

        if hasattr(record, 'request_url'):
            input_data['request_url'] = record.request_url

        if isinstance(record.args, dict):
            for key in record.args:
                if key not in input_data:
                    input_data[key] = record.args[key]
                else:
                    input_data[key + "_"] = record.args[key]
        elif record.name == "uvicorn.access":
            try:
                input_data['method'] = record.args[1]
                input_data['endpoint'] = record.args[2]
                input_data['status'] = record.args[4]
                if input_data['status'] != 200 and input_data['severity'] == logging.getLevelName(logging.INFO):
                    input_data['severity'] = logging.getLevelName(logging.WARNING)
            except:
                pass
        return json.dumps(input_data)

def setup_logging():
    import sys
    import os

    old_stdout = sys.stdout # backup current stdout
    old_stderr = sys.stderr # backup current stdout
    #sys.stdout = open(os.devnull, "w")
    #sys.stderr = open(os.devnull, "w")
    # sys.stdout = old_stdout # reset old stdout

    logger = logging.getLogger()
    logger.setLevel(logging._nameToLevel[os.getenv('LOGLEVEL') or "INFO"])

    ch = logging.StreamHandler()
    ch.setStream(old_stderr)
    if os.getenv('LOGHUMAN') != '1':
        formatter = CustomLoggingFormatter()
        ch.setFormatter(formatter)
    logger.addHandler(ch)
