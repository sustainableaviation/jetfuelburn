# FAQ

## In-Browser Code Editor

### Missing Values

Some return values are currently not shown correctly, such as the dictionary returned by the [`jetfuelburn.aux.allocation.footprint_allocation_by_area`][] function:

```
{'fuel_eco': , 'fuel_premiumeco': 0, 'fuel_business': , 'fuel_first': 0}
```

This is because the dictionary values are `pint` quantities, which are rendered as long float/string combinations:

```
>>> return_dict['fuel_eco']
81.87134502923978 kilogram
```