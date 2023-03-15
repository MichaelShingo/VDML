#! lateFinesEmail.py
#copy data from the excel spreadsheet 
from datetime import datetime

def generateEmail(name, amount, details, date_range, return_time):
    finePlusDays = str(amount)
    dateFormat = '2/9/2023 4:30 PM'
    actualReturn = datetime.strftime(return_time, '%m/%d/%Y %I:%M %p')
    actualReturn = actualReturn.replace('/0', '/').lstrip('0').replace(' 0', ' ')
    if amount == '':
        amount = 0
    daysLate = amount // 25
    if amount == 25:
        finePlusDays += '.00'
    elif amount == 50:
        finePlusDays += f'.00 (past the return time and {str(daysLate - 1)} day late)'
    else:
        finePlusDays += f'.00 (past the return time and {str(daysLate - 1)} days late)'
    if name:
        firstName = name[0:name.index(' ')]
    else:
        firstName = ''
    if date_range:
        scheduledReturn = date_range[date_range.index('-') + 2:]
    else:
        scheduledReturn = ''

    result = """Hi %s,

Our records show you borrowed equipment from the Vitale Digital Media Lab and returned it late (see details below). 

The overdue fine of $%s will be added to your library account by next week, and you may pay it off at the Circulation Desk at that time.

If you have any questions, please feel free to reply to this email or contact the lab manager, David Toccafondi (davidtoc@pobox.upenn.edu, 215-746-2661).

%s

Scheduled return: %s

Actual return: %s""" % (firstName, finePlusDays, details, scheduledReturn, actualReturn)
    return result.replace('&', 'and')




