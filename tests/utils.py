import io
import logging
import os
from contextlib import contextmanager

normal_env = {
    "UCX_RNDV_SCHEME": "put_zcopy",
    "UCX_MEMTYPE_CACHE": "n",
    "UCX_TLS": "rc,cuda_copy,cuda_ipc",
    "CUDA_VISIBLE_DEVICES": "0",
}


def set_env():
    os.environ.update(normal_env)


def more_than_two_gpus():
    import pynvml

    pynvml.nvmlInit()
    ngpus = pynvml.nvmlDeviceGetCount()
    return ngpus >= 2


def get_cuda_visible_devices():
    if "CUDA_VISIBLE_DEVICES" in os.environ:
        return os.environ["CUDA_VISIBLE_DEVICES"]
    else:
        import pynvml

        return "".join(["%d," % d for d in range(pynvml.nvmlDeviceGetCount())])[:-1]


@contextmanager
def captured_logger(logger, level=logging.INFO, propagate=None):
    """Capture output from the given Logger.
    """
    if isinstance(logger, str):
        logger = logging.getLogger(logger)
    orig_level = logger.level
    orig_handlers = logger.handlers[:]
    if propagate is not None:
        orig_propagate = logger.propagate
        logger.propagate = propagate
    sio = io.StringIO()
    logger.handlers[:] = [logging.StreamHandler(sio)]
    logger.setLevel(level)
    try:
        yield sio
    finally:
        logger.handlers[:] = orig_handlers
        logger.setLevel(orig_level)
        if propagate is not None:
            logger.propagate = orig_propagate
