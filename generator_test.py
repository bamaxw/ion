from ion.generators import ChainGenerator, take

source = range(100)
square = lambda x: x ** x
stream = ChainGenerator(source).take(10).map(square).sum()

x = sum(
    map(
        lambda x: x ** x,
        take(
            10,
            iter(source)
        )
    )
)

for val in stream:
    print(val)

print(x)
