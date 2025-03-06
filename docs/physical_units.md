# Working with Physical Units

The `jetfuelburn` package utilises the [`pint` package](https://pint.readthedocs.io/en/stable/) to support physical units in calculations. The `pint` package allows for the definition of physical units and the conversion between them.

To use physical units, simply load the `ureg` object (**u**nit **reg**istry) from the `jetfuelburn` package. You can now start [defining physical quantities](https://pint.readthedocs.io/en/stable/user/defining-quantities.html): 

```python
>>> from jetfuelburn import ureg
>>> 100 * ureg.kg
<Quantity(100.0, 'kg')>
```


!!! warning

    Remember that you must load the `ureg` object from the `jetfuelburn` package to use physical units. Loading the `ureg` object will also load the `pint` package. You **cannot** simply:

    ```python
    import pint
    ureg = pint.UnitRegistry()
    ```

    since this would create _another_ `ureg` object. This documented in the section [Having a Shared Registry](https://pint.readthedocs.io/en/stable/getting/pint-in-your-projects.html#using-pint-in-your-projects) of the `pint` documentation.

The most frequent use-cases of the `ureg` object are:

```python
>>> mass = 100 * ureg.kg
>>> mass.to('lbs')
220.46226218487757 pound
>>> mass.check('[mass]')
True
```

In order to get a list of all available units, you can use the following code:

```python
list(ureg._units.keys())
```

You can search this list for specific units using list comprehensions:

```python
[unit for unit in ureg._units.keys() if "meter" in unit]
```

!!! note

    Note that because of American hegemony in the world of science, `'ton'` refers to a short ton (2000 lbs). If you would instead like to use civilized tons (1000 kg), you can use `'metric_ton'` instead.