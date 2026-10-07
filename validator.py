from urllib.parse import urlparse


ALLOWED_SOURCES = {
    "Books to Scrape",
    "Quotes to Scrape"
}


def validate_record(record):

    problems = []

    source = record.get("source", "")
    name = record.get("name_or_title", "")
    url = record.get("source_url", "")
    price = record.get("price", "")
    rating = record.get("rating", "")

    # Validate source
    if source not in ALLOWED_SOURCES:
        problems.append("invalid_source")

    # Validate name/title
    if not name or not str(name).strip():
        problems.append("missing_name_or_title")

    # Validate URL
    parsed_url = urlparse(str(url))

    if parsed_url.scheme not in {"http", "https"}:
        problems.append("invalid_url")

    # Validate price
    if price != "":

        try:
            if float(price) < 0:
                problems.append("negative_price")
        except (ValueError, TypeError):
            problems.append("invalid_price")

    # Validate rating
    if rating != "":

        try:
            rating_number = int(rating)

            if rating_number < 1 or rating_number > 5:
                problems.append("invalid_rating")

        except (ValueError, TypeError):
            problems.append("invalid_rating")

    return problems