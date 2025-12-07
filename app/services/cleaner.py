import re


def clean_scraped_text(text: str) -> str:
    """
    Better text cleaner for RAG:
    - Removes boilerplate junk
    - Keeps email, phone, addresses, contact info
    - Keeps short lines if they look important
    - Removes duplicates
    """

    if not text:
        return ""

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Remove obvious boilerplate junk (case-insensitive)
    blacklist_patterns = [
        r"© \d{4}",
        r"all rights reserved",
        r"terms and conditions",
        r"privacy policy",
        r"follow us",
        r"newsletter subscribe",
        r"cookie policy",
    ]

    for pattern in blacklist_patterns:
        text = re.sub(pattern, " ", text, flags=re.IGNORECASE)

    # Split text into manageable lines
    raw_lines = re.split(r"[.\n]", text)
    cleaned = []
    seen = set()

    # Patterns to detect contact info
    email_pattern = re.compile(r"\S+@\S+")
    phone_pattern = re.compile(r"\+?\d[\d\s\-]{7,}")
    url_pattern = re.compile(r"(http|www)\S+")

    important_keywords = [
        "contact", "email", "phone", "support", "call",
        "help", "address", "reach us", "get in touch", "chat",
        "whatsapp", "message us"
    ]

    for line in raw_lines:
        line = line.strip()

        if not line:
            continue

        lower_line = line.lower()

        # Detect important lines even if short
        is_important = (
            email_pattern.search(line) or
            phone_pattern.search(line) or
            any(keyword in lower_line for keyword in important_keywords)
        )

        # Keep short lines ONLY if they are important
        if len(line) < 25 and not is_important:
            continue

        # Remove duplicate lines
        if lower_line in seen:
            continue

        seen.add(lower_line)
        cleaned.append(line)

    # Join everything back
    final = ". ".join(cleaned).strip()
    return final
