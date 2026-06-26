"""Celery tasks package for the scraping platform.

Tasks are autodiscovered by the Celery app from this package.
Explicit imports ensure all task modules are registered.
"""

from app.tasks.scraping import execute_scraping  # noqa: F401
