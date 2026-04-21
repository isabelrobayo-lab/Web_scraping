"""Scraping engine module.

Contains the core scraping engine components:
- BrowserManager: Playwright browser lifecycle with stealth configuration
- StealthConfig: Anti-bot techniques (User-Agent pool, delays, session rotation)
- CrawlQueue: URL queue with depth control and deduplication
- DataExtractor: 66-field extraction using Mapa_Selectores
- CaptchaDetector: CAPTCHA detection heuristics
- Backoff: Exponential backoff for HTTP 429 responses
- ScrapingEngine: Main orchestrator
- ProgressPublisher: Redis Pub/Sub progress publishing
"""

from app.engine.backoff import ExponentialBackoff
from app.engine.browser_manager import BrowserManager
from app.engine.captcha_detector import CaptchaDetector
from app.engine.crawl_queue import CrawlItem, CrawlQueue
from app.engine.data_extractor import DataExtractor
from app.engine.progress_publisher import ProgressPublisher
from app.engine.scraping_engine import ScrapingEngine
from app.engine.stealth_config import StealthConfig

__all__ = [
    "BrowserManager",
    "CaptchaDetector",
    "CrawlItem",
    "CrawlQueue",
    "DataExtractor",
    "ExponentialBackoff",
    "ProgressPublisher",
    "ScrapingEngine",
    "StealthConfig",
]
