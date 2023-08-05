def flatRate(details, price):
    return price

def costRate(details, *av, **kw):
    def _cost(x):
        if hasattr(x, "cost"):
            return x.cost()
        else:
            return pFloat("0.0")
    return sum(map(_cost, details))

def markupRate(details, price):
    return costRate(details) + price

handlers = {
    'flat' : flatRate,
    'cost' : costRate,
    'markup' : markupRate,
    }
