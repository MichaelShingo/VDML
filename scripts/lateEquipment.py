import re

def generateEmail(text):
    bookingRegex = re.compile(r'Con\d{6}')
    bookingNum = bookingRegex.findall(text)
    bookingNum = bookingNum[0]
    dateRegex = re.compile(r'\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d\d \w\w - \d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d\d \w\w')
    dateRange = dateRegex.findall(text)

    if len(dateRange) == 0:
        dateRegex = re.compile(r'\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2} \w\w - \d{1,2}:\d{2} \w\w')
        dateRange = dateRegex.findall(text)

    dateRange = dateRange[0]

    ownerIndex = text.index('Owner')
    ownerIndex += 6
    ownerEnd = text.find('(') - 1
    owner = text[ownerIndex:ownerEnd]
    owner = owner.upper().strip()


    dateRangeIndex = text.index(dateRange)
    dateRangeIndex += len(dateRange)
    text = text[dateRangeIndex + 3:]


    barcodeRegex = re.compile(r'\t\d{4}\t') #gets all barcodes
    barcodeList = barcodeRegex.findall(text)
    firstBarcodeIndex = text.index(barcodeList[0])

    firstEquipment = text[:firstBarcodeIndex]
    equipmentList = [firstEquipment]


    equipmentRegex = re.compile(r'\t.{5,}\t') #gets all equipment except first one
    equipmentList.extend(equipmentRegex.findall(text))

    for i in range(1, len(equipmentList)):
        equipmentList[i] = equipmentList[i][:len(equipmentList[i]) - 6]

    for i in range(len(equipmentList)):
        equipmentList[i] = equipmentList[i].strip()
    equipmentString = '\n'.join(equipmentList)
    print(owner, dateRange, bookingNum)
    resultString = """Dear %s,

Our records show that you have equipment still checked out from us.

Please return our equipment or the fine will continue to accumulate and will be issued onto your Penn library account.

-------------------------------------------------------------
%s
%s
Items:
%s
-------------------------------------------------------------


Let us know if you have any concerns or questions.""" % (owner, bookingNum, dateRange, equipmentString)
    return resultString