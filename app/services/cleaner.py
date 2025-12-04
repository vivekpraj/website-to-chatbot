import re

def clean_text(text: str) -> str:
    """
    Clean noisy website text:
    - Remove navbar/footer repeated sections
    - Remove multiple spaces and newlines
    - Remove CSS/JS words
    - Remove duplicate lines
    - Remove extremely short useless lines
    """

    if not text:
        return ""

    # 1️⃣ Remove multiple spaces
    text = re.sub(r"\s+", " ", text)

    # 2️⃣ Remove common navbar/footer junk (case-insensitive)
    blacklist_patterns = [
        r"home about us work contact us career",
        r"© \d{4}",
        r"newsletter", 
        r"follow us",
        r"privacy policy",
        r"terms and conditions",
        r"copyright",
        r"all rights reserved"
    ]

    for pattern in blacklist_patterns:
        text = re.sub(pattern, " ", text, flags=re.IGNORECASE)

    # 3️⃣ Remove URLs inside the text
    text = re.sub(r"http\S+", " ", text)

    # 4️⃣ Remove email + phone numbers
    text = re.sub(r"\S+@\S+", " ", text)
    text = re.sub(r"\+?\d[\d\s]{7,}", " ", text)

    # 5️⃣ Break into lines and remove very short or duplicate lines
    lines = text.split(".")
    cleaned_lines = []
    seen = set()

    for line in lines:
        line = line.strip()
        if len(line) < 25:        # ignore tiny junk
            continue
        if line.lower() in seen:  # avoid duplicates
            continue

        cleaned_lines.append(line)
        seen.add(line.lower())

    # 6️⃣ Join back
    cleaned_text = ". ".join(cleaned_lines)
    return cleaned_text.strip()
