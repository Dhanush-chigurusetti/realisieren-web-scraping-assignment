import re


def clean_text(value):
    """Remove extra whitespace."""

    if value is None:
        return ""

    value = str(value)

    value = re.sub(r"\s+", " ", value)

    return value.strip()


def strip_quotes(value):
    """Remove surrounding quotation marks."""

    value = clean_text(value)

    value = value.strip('"“”\'‘’')

    return value.strip()


def clean_price(value):
    """Convert price such as £51.77 into 51.77."""

    if value is None:
        return ""

    value = clean_text(value)

    value = value.replace("£", "")
    value = value.replace("$", "")
    value = value.replace("€", "")
    value = value.replace(",", "")

    match = re.search(r"\d+(?:\.\d+)?", value)

    if not match:
        return ""

    return float(match.group())


def clean_rating(value):
    """Convert rating words into numbers 1-5."""

    if value is None:
        return ""

    value = clean_text(value).lower()

    rating_map = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5
    }

    for word, number in rating_map.items():

        if word in value:
            return number

    return ""


def clean_tags(value):
    """Clean and normalize tags."""

    if not value:
        return ""

    if isinstance(value, list):
        tags = value
    else:
        tags = str(value).split(";")

    cleaned_tags = []

    for tag in tags:

        tag = clean_text(tag)

        if tag:
            cleaned_tags.append(tag)

    return ";".join(cleaned_tags)


def normalize_url(value):
    """Normalize a URL."""

    if not value:
        return ""

    return clean_text(value).rstrip("/")


def clean_record(record):

    cleaned = record.copy()

    cleaned["source"] = clean_text(
        cleaned.get("source", "")
    )

    cleaned["source_url"] = normalize_url(
        cleaned.get("source_url", "")
    )

    cleaned["name_or_title"] = strip_quotes(
        cleaned.get("name_or_title", "")
    )

    cleaned["category"] = clean_text(
        cleaned.get("category", "")
    )

    cleaned["price"] = clean_price(
        cleaned.get("price", "")
    )

    cleaned["rating"] = clean_rating(
        cleaned.get("rating", "")
    )

    cleaned["author"] = clean_text(
        cleaned.get("author", "")
    )

    cleaned["tags"] = clean_tags(
        cleaned.get("tags", "")
    )

    cleaned["description"] = clean_text(
        cleaned.get("description", "")
    )

    cleaned["scraped_at"] = clean_text(
        cleaned.get("scraped_at", "")
    )

    return cleaned