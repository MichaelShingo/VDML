import pyperclip

def generateEmail(excelText):
    excelRowsList = excelText.split('\n')
    excelListRow = []

    for row in excelRowsList:
        rowList = row.split('\t')
        excelListRow.append(rowList)

    finalText = ''

    for row in excelListRow:
        finalText += '-----------------------------------------\n'
        finalText += row[0] + '\n' + row[1] + '\n' + row[2] + '\n' + row[3] + '\n' + row[4] + '\n' + row[5] + '\n\n' + '-----------------------------------------'
        
    print(finalText)

    pyperclip.copy(finalText)
    return finalText



#0 - Name
#1 - Penn ID
#2 - Email
#3 - Fine
#4 - Booking Number
#5 - Late Equipment
#6 - Booking timeframe
#7 - Actual Return time
#8 - Lab Consultant
#9 - Fine Processing Date

