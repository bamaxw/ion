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
### args
### cache
### dynamodb
### hash
### json
### primes
### string
### time	
### url
### \_class
### bash
### decorators
### env
### injector
### list
### math
### requests
### threading
### typing
### \_import
### benchmark
### dict
### files
### itemstore
### logging
### nlp
### setup
### throttle
### units
