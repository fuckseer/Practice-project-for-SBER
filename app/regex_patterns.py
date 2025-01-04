PARSE_S3_COMPONENTS_PATTERN = r'^(https://[^/]+)/([^/]+)/(.*/)?([^/]+)/?$'
'''
Паттерн извлекает из строк по типу: https://{endpoint_url}/{bucket_name}/{folder}
все ключевые теги строки в следующем формате:
- match.group(1) - endpoint_url
- match.group(2) - bucket_name
- match.group(4) - folder. Данный match всегда возвращает folder, вне зависимости от
  того, насколько глубоко в директории находится финальный folder
'''

PARSE_GPS_TAGS_PATTERN = r"\{1: '([NS])', 2: \((\d+)\.\d+, (\d+)\.\d+, (\d+\.\d+)\), 3: '([EW])', 4: \((\d+)\.\d+, (\d+)\.\d+, (\d+\.\d+)\)"
'''
Паттерн извлекает из строкового представления словаря ExifTags.IFD.GPSInfo в следующем формате:
- match.group(1) - Полярность значения широты N/S (North/South)
- match.group(2) - Градусы широты
- match.group(3) - Минуты широты
- match.group(4) - Секунды широты

- match.group(5) - Полярность значения долготы W/E (West/East)
- match.group(6) - Градусы долготы
- match.group(7) - Минуты долготы
- match.group(8) - Секунды долготы
'''
