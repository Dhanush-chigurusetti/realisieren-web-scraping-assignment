import logging
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from scraper import scrape_books, scrape_quotes
from cleaner import clean_record
from validator import validate_record
from deduplicator import deduplicate_records
from writer import write_csv, write_summary


LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "scraper.log"


def setup_logging():

    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(message)s"
        ),
        handlers=[
            logging.FileHandler(
                LOG_FILE,
                encoding="utf-8"
            ),
            logging.StreamHandler()
        ]
    )


def main():

    setup_logging()

    logger = logging.getLogger(__name__)

    start_time = datetime.now(timezone.utc)

    logger.info("Scraping job started.")

    raw_records = []

    raw_books = 0
    raw_quotes = 0

    # -----------------------------
    # SCRAPE
    # -----------------------------

    try:

        books = scrape_books()

        raw_books = len(books)

        raw_records.extend(books)

    except Exception as error:

        logger.exception(
            "Books scraper failed: %s",
            error
        )

    try:

        quotes = scrape_quotes()

        raw_quotes = len(quotes)

        raw_records.extend(quotes)

    except Exception as error:

        logger.exception(
            "Quotes scraper failed: %s",
            error
        )

    logger.info(
        "Total raw records: %s",
        len(raw_records)
    )

    # -----------------------------
    # CLEAN
    # -----------------------------

    cleaned_records = []

    for record in raw_records:

        try:

            cleaned = clean_record(record)

            cleaned_records.append(cleaned)

        except Exception as error:

            logger.warning(
                "Cleaning failed: %s",
                error
            )

    # -----------------------------
    # VALIDATE
    # -----------------------------

    valid_records = []

    rejected_count = 0

    rejection_reasons = Counter()

    for record in cleaned_records:

        problems = validate_record(record)

        if problems:

            rejected_count += 1

            for problem in problems:
                rejection_reasons[problem] += 1

            logger.warning(
                "Rejected record: %s",
                problems
            )

            continue

        valid_records.append(record)

    # -----------------------------
    # DEDUPLICATE
    # -----------------------------

    final_records, duplicate_count = deduplicate_records(
        valid_records
    )

    # -----------------------------
    # WRITE CSV
    # -----------------------------

    write_csv(final_records)

    # -----------------------------
    # SUMMARY
    # -----------------------------

    end_time = datetime.now(timezone.utc)

    duration = (
        end_time - start_time
    ).total_seconds()

    cleaned_by_source = Counter(
        record["source"]
        for record in cleaned_records
    )

    final_by_source = Counter(
        record["source"]
        for record in final_records
    )

    summary = {
        "raw_records": {
            "Books to Scrape": raw_books,
            "Quotes to Scrape": raw_quotes,
            "total": len(raw_records)
        },

        "cleaned_records": {
            "Books to Scrape": cleaned_by_source.get(
                "Books to Scrape",
                0
            ),
            "Quotes to Scrape": cleaned_by_source.get(
                "Quotes to Scrape",
                0
            ),
            "total": len(cleaned_records)
        },

        "rejected_records": {
            "total": rejected_count,
            "by_reason": dict(rejection_reasons)
        },

        "duplicates": duplicate_count,

        "final_records": {
            "Books to Scrape": final_by_source.get(
                "Books to Scrape",
                0
            ),
            "Quotes to Scrape": final_by_source.get(
                "Quotes to Scrape",
                0
            ),
            "total": len(final_records)
        },

        "started_at": start_time.isoformat(),

        "finished_at": end_time.isoformat(),

        "duration_seconds": duration
    }

    write_summary(summary)

    logger.info(
        "Final records: %s",
        len(final_records)
    )

    logger.info(
        "Scraping job finished successfully."
    )


if __name__ == "__main__":
    main()