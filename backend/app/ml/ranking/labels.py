STATUS_RELEVANCE = {
    "hired": 4,
    "interview": 3,
    "shortlisted": 2,
    "reviewing": 1,
    "applied": 0,
    "rejected": 0
}


def get_relevance_label(status: str) -> int:
    """
    Convert application status into a relevance score.
    """

    if not status:
        return 0

    return STATUS_RELEVANCE.get(
        status.lower(),
        0
    )