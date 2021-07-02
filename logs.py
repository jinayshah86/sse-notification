import logging

log = logging.getLogger("sse")
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
sh.setFormatter(formatter)
log.addHandler(sh)

__all__ = ["log"]
