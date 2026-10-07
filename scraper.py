import logging
import time
from datetime import datetime, timezone
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


BOOKS_URL = "https://books.toscrape.com/"
QUOTES_URL = "https://quotes.toscrape.com/"


logger = logging.getLogger(__name__)


def create_session():
    """Create a requests session with a browser-like User-Agent."""
    session = requests.Session()

    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/154.0.0.0 Safari/537.36"
        )
    })

    return session


def fetch_page(session, url):
    """Fetch a web page with basic retry handling."""

    retries = 3
    retry_status_codes = {429, 500, 502, 503, 504}

    for attempt in range(1, retries + 1):

        try:
            response = session.get(url, timeout=15)

            if response.status_code in retry_status_codes:
                logger.warning(
                    "Retryable status %s for %s (attempt %s)",
                    response.status_code,
                    url,
                    attempt
                )

                time.sleep(2)
                continue

            response.raise_for_status()

            response.encoding = "utf-8"

            return response.text

        except requests.RequestException as error:

            logger.error(
                "Request failed for %s: %s",
                url,
                error
            )

            if attempt == retries:
                return None

            time.sleep(2)

    return None


def scrape_books():
    """Scrape all books from Books to Scrape."""

    session = create_session()

    current_url = BOOKS_URL
    records = []

    while current_url:

        logger.info("Scraping Books page: %s", current_url)

        html = fetch_page(session, current_url)

        if html is None:
            logger.error("Failed page: %s", current_url)
            break

        soup = BeautifulSoup(html, "lxml")

        books = soup.select("article.product_pod")

        for book in books:

            try:
                title_element = book.select_one("h3 > a")
                price_element = book.select_one("p.price_color")
                rating_element = book.select_one("p.star-rating")

                if title_element is None:
                    continue

                title = title_element.get("title", "")
                detail_url = urljoin(
                    current_url,
                    title_element.get("href", "")
                )

                price = (
                    price_element.get_text(strip=True)
                    if price_element
                    else ""
                )

                rating = (
                    " ".join(rating_element.get("class", []))
                    if rating_element
                    else ""
                )

                records.append({
                    "source": "Books to Scrape",
                    "source_url": detail_url,
                    "name_or_title": title,
                    "category": "",
                    "price": price,
                    "rating": rating,
                    "author": "",
                    "tags": "",
                    "description": "",
                    "scraped_at": datetime.now(
                        timezone.utc
                    ).isoformat()
                })

            except Exception as error:

                logger.warning(
                    "Failed to parse a book: %s",
                    error
                )

        next_link = soup.select_one("li.next > a")

        if next_link:
            next_href = next_link.get("href")

            if next_href:
                current_url = urljoin(
                    current_url,
                    next_href
                )
            else:
                current_url = None
        else:
            current_url = None

        time.sleep(0.5)

    logger.info(
        "Books scraping finished. Records: %s",
        len(records)
    )

    return records


def scrape_quotes():
    """Scrape all quotes from Quotes to Scrape."""

    session = create_session()

    current_url = QUOTES_URL
    records = []

    while current_url:

        logger.info("Scraping Quotes page: %s", current_url)

        html = fetch_page(session, current_url)

        if html is None:
            logger.error("Failed page: %s", current_url)
            break

        soup = BeautifulSoup(html, "lxml")

        quotes = soup.select("div.quote")

        for quote in quotes:

            try:
                text_element = quote.select_one("span.text")
                author_element = quote.select_one("small.author")
                tag_elements = quote.select("a.tag")

                if text_element is None:
                    continue

                quote_text = text_element.get_text(
                    " ",
                    strip=True
                )

                author = (
                    author_element.get_text(
                        " ",
                        strip=True
                    )
                    if author_element
                    else ""
                )

                tags = ";".join(
                    tag.get_text(
                        " ",
                        strip=True
                    )
                    for tag in tag_elements
                )

                records.append({
                    "source": "Quotes to Scrape",
                    "source_url": current_url,
                    "name_or_title": quote_text,
                    "category": "",
                    "price": "",
                    "rating": "",
                    "author": author,
                    "tags": tags,
                    "description": "",
                    "scraped_at": datetime.now(
                        timezone.utc
                    ).isoformat()
                })

            except Exception as error:

                logger.warning(
                    "Failed to parse a quote: %s",
                    error
                )

        next_link = soup.select_one("li.next > a")

        if next_link:
            next_href = next_link.get("href")

            if next_href:
                current_url = urljoin(
                    current_url,
                    next_href
                )
            else:
                current_url = None
        else:
            current_url = None

        time.sleep(0.5)

    logger.info(
        "Quotes scraping finished. Records: %s",
        len(records)
    )

    return records