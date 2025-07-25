from flask import jsonify
import logging

logger = logging.getLogger(__name__)

class APIError(Exception):
    status_code = 500
    message = "An unexpected error occurred."

    def __init__(self, message=None, status_code=None, payload=None):
        super().__init__(message)
        if message is not None:
            self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = {'message': self.message}
        if self.payload is not None:
            rv['payload'] = self.payload
        return rv

def handle_api_error(error):
    if isinstance(error, APIError):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        logger.warning(f"API Error: {error.status_code} - {error.message} - Details: {error.payload}")
    else:
        response = jsonify({"message": "An internal server error occurred."})
        response.status_code = 500
        logger.exception(f"Unhandled exception: {error}")
    return response
