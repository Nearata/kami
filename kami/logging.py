import logging

from pathlib import Path


Path("logs").mkdir(exist_ok=True)

log = logging.getLogger("kami")

file_formatter = logging.Formatter(
    fmt="[%(asctime)s] [%(name)s/%(levelname)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
console_formatter = logging.Formatter(fmt="[%(name)s/%(levelname)s]: %(message)s")

file_handler = logging.FileHandler(filename="logs/kami.log", mode="a")
console_handler = logging.StreamHandler()

file_handler.setFormatter(file_formatter)
console_handler.setFormatter(console_formatter)

log.addHandler(file_handler)
log.addHandler(console_handler)
