#! Takes text input and generates a csv
import pyperclip, re, datetime

def generateCSV(text):
    todayDate = datetime.datetime.today().strftime('%m/%d/%Y')
    bookingRegex = re.compile(r'Con\d{6}')
    bookingNum = bookingRegex.findall(text)
    bookingNum = bookingNum[0]
    dateRegex = re.compile(r'\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d\d \w\w - \d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d\d \w\w')
    dateRange = dateRegex.findall(text)

    staffRegex = re.compile(r'By \w+')
    staffName = staffRegex.findall(text)[1][3:]

    if len(dateRange) == 0:
        dateRegex = re.compile(r'\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2} \w\w - \d{1,2}:\d{2} \w\w')
        dateRange = dateRegex.findall(text)

    dateRange = dateRange[0]

    ownerIndex = text.index('Owner')
    ownerIndex += 6
    ownerEnd = text.find('(') - 1
    owner = text[ownerIndex:ownerEnd]
    owner = owner.strip()

    dateRangeIndex = text.index(dateRange)
    dateRangeIndex += len(dateRange)
    text = text[dateRangeIndex + 3:]

    returnTimeRegex = re.compile(r'\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d\d \w\w')
    returnTime = returnTimeRegex.findall(text)[1]

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
    equipmentString = 'Late: ' + ' | '.join(equipmentList)
    result = '%s\t\t\t\t%s\t%s\t%s\t%s\t%s\t%s' % (owner, bookingNum, equipmentString, dateRange, returnTime, staffName, todayDate)
    #pyperclip.copy(result)
    equipmentString = equipmentString.replace('\t', '')
    return owner, bookingNum, equipmentString, dateRange, returnTime, staffName, todayDate