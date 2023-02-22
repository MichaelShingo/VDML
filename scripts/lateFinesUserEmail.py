#! lateFinesEmail.py
#copy data from the excel spreadsheet 

import pyperclip

def generateEmail(name, amount, details, date_range, return_time):
    finePlusDays = str(amount)
    if amount == '':
        amount = 0
    daysLate = amount // 25
    if amount == 25:
        finePlusDays += '.00 (1 day'
    else:
        finePlusDays += '.00 (' + str(daysLate) + ' days'
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

The overdue fine of $%s late @ $25/day) will be added to your library account by next week, and you may pay it off at the Circulation Desk at that time.

If you have any questions, please feel free to reply to this email or contact the lab manager, David Toccafondi (davidtoc@pobox.upenn.edu, 215-746-2661).

%s

Scheduled return: %s

Actual return: %s""" % (firstName, finePlusDays, details, scheduledReturn, return_time)
    return result.replace('&', 'and')




