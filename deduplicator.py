import hashlib
import re


def normalize_for_fingerprint(value):
    """Normalize text for duplicate detection."""

    value = str(value).lower()

    value = re.sub(
        r"[^\w\s]",
        " ",
        value
    )

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value.strip()


def create_fingerprint(record):

    source = record.get("source", "")

    name = normalize_for_fingerprint(
        record.get("name_or_title", "")
    )

    author = normalize_for_fingerprint(
        record.get("author", "")
    )

    if source == "Books to Scrape":

        identifying_text = (
            f"{source}|{name}"
        )

    elif source == "Quotes to Scrape":

        quote_part = name[:50]

        identifying_text = (
            f"{source}|{author}|{quote_part}"
        )

    else:

        identifying_text = (
            f"{source}|{name}|{author}"
        )

    return hashlib.sha256(
        identifying_text.encode("utf-8")
    ).hexdigest()


def deduplicate_records(records):

    unique_records = []
    seen = set()
    duplicate_count = 0

    for record in records:

        fingerprint = create_fingerprint(record)

        if fingerprint in seen:

            duplicate_count += 1

            continue

        seen.add(fingerprint)

        unique_records.append(record)

    return unique_records, duplicate_count