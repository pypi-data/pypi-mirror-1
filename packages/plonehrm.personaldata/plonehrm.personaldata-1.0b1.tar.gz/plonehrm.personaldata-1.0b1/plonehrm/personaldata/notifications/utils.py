from DateTime import DateTime

def next_anniversary(employee):
    """Helper function to get the next anniversary of the employee
    """
    birthday = employee.personal.getBirthDate()
    if birthday is None:
        return None
    now = DateTime().earliestTime()
    anniversary = DateTime(now.year(), birthday.month(), birthday.day())
    if now > anniversary:
        anniversary = DateTime(now.year()+1, birthday.month(), birthday.day())
    return anniversary
