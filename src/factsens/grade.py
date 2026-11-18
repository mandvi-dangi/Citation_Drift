def grade(parsed_answer, gold):
    """'C' correct, 'I' incorrect (includes unparseable output), 'N' not attempted (explicit NS)."""
    if parsed_answer == "NS":
        return "N"
    if parsed_answer is None:
        return "I"
    return "C" if parsed_answer == gold else "I"
