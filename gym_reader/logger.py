import logging
import structlog
from gym_reader.settings import get_settings
from colorlog import ColoredFormatter

# Create a console handler for terminal output
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Define the console formatter based on the environment
if get_settings().is_dev():
    console_formatter = ColoredFormatter(
        "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
    )
else:
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

console_handler.setFormatter(console_formatter)

# Configure structlog
structlog.configure(
    processors=[
        structlog.processors.JSONRenderer()
        if get_settings().is_prod()
        else structlog.dev.ConsoleRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)


# Function to get a logger instance
def get_logger(name: str):
    logger = structlog.get_logger(name)
    if get_settings().is_prod():
        logging.basicConfig(handlers=[console_handler], level=logging.INFO)
    else:
        logging.basicConfig(handlers=[console_handler], level=logging.DEBUG)
    return logger


__all__ = ["get_logger"]

# Example usage to test logging
if __name__ == "__main__":
    logger = get_logger(__name__)
    logger.info("This is a test log message.")
