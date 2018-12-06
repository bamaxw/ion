# ion

# ion.time
Root time module containing helper functions and classes for dealing with time and dates
## ts
```python
ts()
```
Get current UNIX timestamp in seconds as an integer
## pts
```python
pts()
```
Get current UNIX timestamp in seconds as a fraction
## msts
```python
msts()
```
Get current UNIX timestamp in milliseconds as an integer
## dt_to_ts
```python
dt_to_ts(date_time: 'datetime.datetime')
```
Convert datetime object to UNIX timetsamp
## to_midnight
```python
to_midnight(date_time: 'datetime.datetime')
```

Round the provided datetime object to the last day
Usage:
    >>> to_midnight(datetime.strptime('14 Aug 1993 10:21', '%d %b %Y %H:%M')).strftime('%d %b %Y %H:%M')
    "14 Aug 1993 00:00"

## format_seconds
```python
format_seconds(seconds: float, _format: str = '%mm:%ss.%msms')
```

Formats a number of seconds into a formatted string
Usage:
    >>> format_seconds(10)
    '00m:10s.000ms'
    >>> format_seconds(110.24)
    '01m:50s.240ms'
    >>> format_seconds(3601.52, _format='%h:%m:%s.%ms')
    '01:00:01.520'

