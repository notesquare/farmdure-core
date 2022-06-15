# remove leap days
def get_index_of_year(dt):
    if dt.is_leap_year and dt.day_of_year >= 60:
        return dt.day_of_year - 2
    return dt.day_of_year - 1
