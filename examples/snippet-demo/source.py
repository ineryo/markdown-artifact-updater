# snippet:start normalize-name
def normalize_name(value: str) -> str:
    """Create a presentation-safe display value."""
    return " ".join(value.split()).title()


# snippet:end normalize-name
