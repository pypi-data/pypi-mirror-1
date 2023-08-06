from DateTime import DateTime


def next_anniversary(employee, now=None):
    """Helper function to get the next anniversary of the employee

    >>> class DummyPersonal(object):
    ...     def __init__(self, birthdate=''):
    ...         self.birthdate = birthdate
    ...     def getBirthDate(self):
    ...         return self.birthdate
    >>> class DummyEmployee(object):
    ...     def __init__(self, birthdate=None):
    ...         self.personal = DummyPersonal(birthdate)
    >>> emp = DummyEmployee()
    >>> next_anniversary(emp) is None
    True

    Let's take a normal birthday:

    >>> emp.personal.birthdate = DateTime('1976/01/27')
    >>> next_anniversary(emp, now=DateTime('1999-01-12'))
    DateTime('1999/01/27')
    >>> next_anniversary(emp, now=DateTime('1999-02-12'))
    DateTime('2000/01/27')

    Having a birthday at leap day (29 February) should work too).  We
    cheat by setting the anniversay to the 28th of February then.

    >>> emp.personal.birthdate = DateTime('1984/02/29')
    >>> next_anniversary(emp, now=DateTime('1999-02-12'))
    DateTime('1999/02/28')

    Of course when this year *is* a leap year, then 29 February is
    fine.

    >>> next_anniversary(emp, now=DateTime('2004-02-12'))
    DateTime('2004/02/29')
    >>> next_anniversary(emp, now=DateTime('2004-03-12'))
    DateTime('2005/02/28')
    >>> next_anniversary(emp, now=DateTime('2005-02-12'))
    DateTime('2005/02/28')
    >>> next_anniversary(emp, now=DateTime('2005-03-12'))
    DateTime('2006/02/28')

    """
    birth_date = employee.personal.getBirthDate()
    if birth_date is None:
        return None
    # When testing we want to make sure that the tests keep passing,
    # also next year, and in the next leap year.  So we allow passing
    # a parameter 'now'.
    if not now:
        now = DateTime().earliestTime()
    birth_month = birth_date.month()
    birth_day = birth_date.day()
    if not now.isLeapYear() and birth_month == 2 and birth_day == 29:
        # This is a leap day, but it is not a leap year.
        birth_day = 28
    anniversary = DateTime(now.year(), birth_month, birth_day)
    if now > anniversary:
        birth_day = birth_date.day()
        next_year = DateTime(now.year()+1, 1, 1)
        if not next_year.isLeapYear() and birth_month == 2 and birth_day == 29:
            # This is a leap day, but it is not a leap year.
            birth_day = 28
        anniversary = DateTime(next_year.year(), birth_month, birth_day)

    return anniversary
