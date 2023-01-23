#! lateFinesEmail.py
#copy data from the excel spreadsheet 

import pyperclip

def generateEmail(text):
    textList = text.split('\t')
    fine = textList[3].strip()
    finePlusDays = fine
    fineInt = int(fine[1:])
    daysLate = fineInt // 25
    if fine == '$25':
        finePlusDays += '.00 (1 day'
    else:
        finePlusDays += '.00 (' + str(daysLate) + ' days'
    name = textList[0]
    firstName = name[0:name.index(' ')]
    equipment = textList[5][6:]
    scheduledReturn = textList[6]
    scheduledReturn = scheduledReturn[scheduledReturn.index('-') + 2:]
    actualReturn = textList[7]
    result = """Hi %s,

Our records show you borrowed equipment from the Vitale Digital Media Lab and returned it late (see details below). 

The overdue fine of %s late @ $25/day) will be added to your library account by next week, and you may pay it off at the Circulation Desk at that time.

If you have any questions, please feel free to reply to this email or contact the lab manager, David Toccafondi (davidtoc@pobox.upenn.edu, 215-746-2661).

Details: Borrowed %s. 
Scheduled return: %s. Actual return: %s.
    """ % (firstName, finePlusDays, equipment, scheduledReturn, actualReturn)

    pyperclip.copy(result)

    return result



