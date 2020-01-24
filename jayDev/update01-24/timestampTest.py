from datetime import datetime


dateTimeObj = datetime.now()
print(dateTimeObj)

timestampStr = dateTimeObj.strptime(str(dateTimeObj), '%Y-%m-%d %H:%M:%S.%f').strftime('%s.%f')
millise = int(float(timestampStr) * 1000)
print(millise)
