# Ion

## Installation
Install ion package using pip
```
pip install https://github.com/bamaxw/ion/archive/master.zip
```
or pipenv
```
pipenv install https://github.com/bamaxw/ion/archive/master.zip
```

If you wish to install an older version of the package or a different development branch
```
pip install https://github.com/bamaxw/ion/archive/<version or branch>.zip
```

## Usage
```python
from ion.url import parse, domain
url = 'https://www.google.com/search?q=python'
dom = domain(url)
query = parse(url, ['query'], as_dict=True)
print('Domain:', dom, 'and query:', query)
```
```
Domain: google.com and query {'query': {'q': 'python'}}
```

## Modules
1. args
2. cache
3. dynamodb
4. hash
5. json
7. primes
8. string
9. time	
10. url
11. \_class
12. bash
13. decorators
15. env
16. injector
17. list
18. math
19. requests
20. threading
21. typing
22. \_import
23. benchmark
24. dict
25. files
26. itemstore
27. logging
28. nlp
29. setup
30. throttle
31. units
