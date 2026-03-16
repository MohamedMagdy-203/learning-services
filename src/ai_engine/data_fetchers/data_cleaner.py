import re


def clean_content(raw_content: str) -> str:
    text = raw_content

    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)

    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)

    text = re.sub(r"<[^>]+>", "", text)

    text = re.sub(r"https?://\S+", "", text)

    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)

    text = re.sub(r"\*{1,3}([^\*\n]+)\*{1,3}", r"\1", text)
    text = re.sub(r"_{1,2}([^_\n]+)_{1,2}", r"\1", text)

    text = re.sub(r"^[-\*]{3,}\s*$", "", text, flags=re.MULTILINE)

    boilerplate_patterns = [
        r"cookie preferences.*",
        r"privacy policy.*",
        r"terms of service.*",
        r"all rights reserved.*",
        r"sign up.*",
        r"log in.*",
        r"subscribe.*",
        r"share this.*",
        r"follow us.*",
        r"get our free app.*",
    ]
    for pattern in boilerplate_patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    text = re.sub(r"\n{3,}", "\n\n", text)

    lines = [line.strip() for line in text.splitlines()]

    lines = [line for line in lines if len(line) >= 20 or line == ""]

    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()
