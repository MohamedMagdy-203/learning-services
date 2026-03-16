_COURSE_DOMAINS = {
    "coursera.org",
    "udemy.com",
    "edx.org",
    "pluralsight.com",
    "linkedin.com",
    "app.datacamp.com/learn/courses/",
}
_VIDEO_DOMAINS = {"youtube.com", "youtu.be"}


def classify_source(url: str) -> str:
    """Classify a source URL into: course | video | blog"""
    lowered = url.lower()
    for domain in _COURSE_DOMAINS:
        if domain in lowered:
            return "course"
    for domain in _VIDEO_DOMAINS:
        if domain in lowered:
            return "video"
    return "blog"
