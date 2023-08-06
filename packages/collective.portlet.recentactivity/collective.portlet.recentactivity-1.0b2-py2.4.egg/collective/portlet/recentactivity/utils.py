def compute_time(absolute_seconds):
    # compute days, hours, and minutes from seconds.
    absolute_minutes = absolute_seconds/60
    days = absolute_minutes/1440
    hours = absolute_minutes/60 - (days * 24)
    minutes = absolute_minutes - (hours * 60) - (days * 24 * 60)
    return {'days': days, 'hours': hours, 'minutes': minutes}
