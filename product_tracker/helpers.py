def format_time_delta(delta):
    """Generates a string representation of a time delta object

    Args:
        delta (timedelta): timedelta object

    Returns:
        string: formatted string to display time delta
    """
    SECONDS_IN_MINUTE = 60
    MINUTES_IN_HOUR = 60 * SECONDS_IN_MINUTE

    seconds = delta.total_seconds()
    hours, remainder = divmod(delta.total_seconds(), MINUTES_IN_HOUR)
    minutes, seconds = divmod(remainder, SECONDS_IN_MINUTE)

    seconds, minutes, hours = round(seconds), round(minutes), round(hours)

    if hours:
        return f"{hours} hours, {minutes} minutes, {seconds} seconds"
    elif minutes:
        return f"{minutes} minutes, {seconds} seconds"
    elif seconds:
        return f"{seconds} seconds"
    else:
        return ""
