LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "filters": [],
        },
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": "django.log",
            "formatter": "standard",
        },
    },
    "loggers": {
        "django": {
            "level": "INFO",
            "handlers": [
                "file",
                "console",
            ],
            "propagate": False,
        },
        "django.db.backends": {
            "level": "DEBUG",
            "handlers": [
                "file",
                "console",
            ],
            "propagate": False,
        },
        "django.server": {
            "level": "INFO",
            "handlers": [
                "file",
                "console",
            ],
            "propagate": False,
        },
        "daphne.server": {
            "level": "INFO",
            "handlers": ["file", "console"],
            "propagate": False,
        },
        "django.request": {
            "level": "INFO",
            "handlers": ["file", "console"],
            "propagate": False,
        },
        "django.template": {
            "level": "INFO",
            "handlers": [
                "file",
                "console",
            ],
            "propagate": False,
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file"],
    },
}
