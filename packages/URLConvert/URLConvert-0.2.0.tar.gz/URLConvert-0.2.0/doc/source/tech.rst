Start off with a ``RuleSet`` object which holds a collection of rules. Use its ``add()`` method to add rules to the set. It will raise an ``InvalidRuleException`` is the rule isn't derived from ``Rule``.

The standard type of rule to use is a ``StandardRule`` derived from ``Rule``. When a ``StandardRule`` is passed a rule string an instance of ``StandardRuleHandler`` is created.  Its ``split()`` method splits the rule and passes each section to a different handler. Scheme, domain, port and path are handled by ``StandardSchemeHandler``, ``StandardDomainHandler``, ``StandardPortHandler`` and ``StandardPathHandler`` respectively. These handlers are arranged into a ConversionKit ``Group`` object and returned to be processed by the Rule.

The rule then procedes to construct two ConversionKit schema, a ``to_vars_schema`` to handle
URL matching and a ``to_url_schema`` to handle URL building.

Matching
========

The ``to_url_schema`` is set up with the following pre_handlers:

``StandardURLSplitter().split``
    Splits the URL being tested into components to be handled by each of the standard handlers for that part of the URL and returns a conversion object containing a dictionary with ``'scheme'``, ``'domain'``, ``'port'`` and ``'path'`` as the keys and their string values as the values.

The values are then converted by the main ``Group`` we just set up to handle each of the parts of the URL. Each handler returns a dictionary of the variables it managed to match and the results are run through the following post_handlers:

``merge``:
    Takes the dictionary of dictionaries and compares the variables. If the same variable comes from different parts of the URL with different values, clearly the match hasn't worked. The return value is a merged dictionary of variables with duplicates removed.

``Add(add)``
    Only used if an add dictionary has been specified when defining the rule. This simply adds the variables to the existing result. But it will raise an Exception if the key already exists. XXX This should have been checked earlier.

``filter``
    We are not speciying a filter at the moment, so ignoring XXX

If the tests get to this point, the rule matches and the dictionary is
returned. Otherwise the next rule is tried. If no rules match then the URL
can't be matched.

Building
========

Building happens in an identical way but with different pre- and post- handlers.

``Duplicate(types, remove=add)``
    First checks to see if the rule has an ``add`` dictionary. If it does it checks the build variables exist with the same values in the add dictionary, and if they do it removes them from the input because they don't need to be considered for this rule.
   XXX This should be split into remove() and duplicate()
    For each part of the URL, all the remaining variables are duplicated because at this stage we don't know which part of the rule will contain which variables so we better give every part every variable to check.

Now the URL part handlers are run again, each with a copy of all the variables. They each check whether it is possible to get the value required from the URL which was entered. Rather than simply returning the variables they have been able to match, the part handlers return a tuple with the values (original variables, value they were matching against, keys matched). 

The results now need putting back together, this is done with the post handlers:

``Join(types)``
    This checks that each of the URL parts return the same values for their original variables then it builds an input list of keys from the first original values tuple returned. At this point, for the rule to be valid, each of the keys must be present in at least one of the keys matched results from the handlers. If all the keys can be matched at some part of the handler then the rule matches and the value they were matching against part are obtained abd joined back together to form a valid URL. The port is hidden if possible (ie if the scheme is already the default for the one used.

That's it, so why doesn't it work!


