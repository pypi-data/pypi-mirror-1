import calendar
import datetime
import operator
import math
from cPickle import loads

from xapian import MatchDecider


class TermCountMatchSpy(MatchDecider):
    """Pure python implementation of term counting match decider that
    should appear in the xapian bindings with the release of 1.1.

    'prefixes': iterable of prefix names strings

    'prefix_dictionary': mapping of prefix names to short prefixes
    normally passed in by Xaql when calling Xaql.term_counter
    """

    def __init__(self, prefixes, prefix_dictionary):
        MatchDecider.__init__(self)
        self.documents_seen = 0
        self.terms_seen = 0
        self.terms = dict((k, {}) for k in prefixes)
        self.prefix_dictionary = prefix_dictionary

    def __call__(self, doc):
        self.documents_seen += 1

        for prefix_name in self.terms:
            terms = self.terms[prefix_name]
            if prefix_name not in self.prefix_dictionary:
                continue
            prefix_code = self.prefix_dictionary[prefix_name]
            prefix_len = len(prefix_code)
            for term in doc:
                if prefix_code in term.term[0:prefix_len]:
                    self.terms_seen += 1
                    term = term.term[prefix_len:]
                    terms[term] = terms.get(term, 0) + 1
        return True

    def get_top_terms(self, prefix, maxterms=10):
        return dict(sorted(
            self.terms[prefix].items(),
            key=operator.itemgetter(1),
            reverse=True,
        )[0:maxterms])


class SchemaValueCountMatchSpy(MatchDecider):
    """Count values in xapian based on a schema.

    :param schema: The schema that defines which values to count, and
    whether they are atoms, sequences, or mappings.

    :param backend: The xapian backend used to resolve value name to
    number mapping.
    """

    def __init__(self, schema, database, facet_on=None):
        MatchDecider.__init__(self)
        self.documents_seen = 0
        self.values_seen = 0
        self.values = dict()
        self.schema = schema
        self.database = database
        self.facet_on = facet_on

        for name, attr in schema.__attributes__.items():
            if attr.value_field:
                if facet_on:
                    if attr.name not in facet_on:
                        continue
                self.values[name] = {}

    def _tally(self, valname, value):
        if value:
            vd = self.values[valname]
            vd[value] = vd.get(value, 0) + 1
            self.values_seen += 1

    def __call__(self, doc):
        self.documents_seen += 1

        for valname in self.values:
            attr = self.schema.__attributes__[valname]
            valno = self.database.values[valname]
            value = doc.get_value(valno)
            if not value:
                continue
            if not attr.sortable:
                value = loads(value)
            if value:
                if attr.sequence:
                    for v in value:
                        self._tally(valname, v)
                elif attr.mapping:
                    pass # not sure...
                else:
                    self._tally(valname, value)
        return True

    def top_values(self, valname, maxvalues=None):
        top_values = sorted(
            self.values[valname].items(),
            key=operator.itemgetter(1),
            reverse=True,
        )
        if maxvalues:
            top_values = top_values[0:maxvalues]
        return top_values

    def score_categorization(self, valname, desired_categories=None):
        """Return a scoring on this value with the desired number
        categories.  Lower is better.

        Added the values_seen concept here and in the ValueCountMatchSpy
        because it seems that the current implementation in c++ in the
        matchspy branch is severely broken for multivalued values.
        """
        score = 0.0
        categories = self.values[valname]
        desired_categories = desired_categories or len(categories)
        avg = float(self.values_seen) / desired_categories
        uncounted = self.values_seen

        for category, count in categories.items():
            uncounted -= count
            score += math.pow(count - avg, 2)
        assert uncounted >= 0, "Uncounted should never go negative"
        if uncounted:
            score += math.pow(uncounted - avg, 2)

        # normalize
        score /= math.pow(self.values_seen, 2)

        # bias towards exact number of categories requested
        score += 0.01 * math.pow(desired_categories - len(categories), 2)

        return score

    def build_numeric_ranges(self, valname, max_ranges, quantize=None):
        """
        Given a value name *valname*, the desired number of ranges
        and a quantization factor, returns a set of (low,high) range
        tuples to cover the range of values present.

        You may get back fewer than *max_ranges* if the quantization
        doesn't fit nicely.

        When no quantization factor is supplied a *max_ranges* ranges
        are return such that the value are evenly distributed accross them.
        (As in the C++ implementation in the match spies branch.)
        """

        if max_ranges < 1:
            return []

        # Make a list of all the values (with copies according to freq)
        values = [([float(v)] * f)
                  for v, f in self.values[valname].items()]
        # Collapse sub-lists and sort
        values = reduce(operator.add, sorted(values))

        count = len(values)
        bucket_size = int(count / max_ranges)
        if count % max_ranges and bucket_size > 1:
            bucket_size += 1


        quant_floor = lambda value, quant: value - (value % quant)
        quant_ceil = lambda value, quant: value if not (value % quant) \
            else value + (quant - value % quant)

        buckets = []
        if quantize:
            bottom = quant_floor(values[0], quantize)
            top = quant_ceil(values[-1], quantize)
            _range = top - bottom

            steps = int(math.floor(_range / float(quantize)))
            if max_ranges > steps:
                max_ranges = steps
            step_size = quant_floor(_range / max_ranges, quantize)

            base = bottom
            for n in range(max_ranges-1):
                buckets.append((base, base + step_size))
                base += step_size
            buckets.append((base, top))
        else:
            starts = map(lambda v: (v * bucket_size), range(0, max_ranges))
            ends = map(lambda v: (v + bucket_size), starts)
            ends[-1] = count
            buckets = [(values[s], values[e-1]) for s, e in zip(starts, ends)]

        return buckets

    def build_date_ranges(self, valname=None, future=False,
                          from_date=None, months=12):
        """Return a set of graduated date ranges forward or back from
        *from_date*.

        :param valname: Optional value slot name.  When provided, any
                        facets not matching values in the search
                        results will be filtered.  TODO:sw implement
                        the filtering.

        :param future: Defaults to False.  When true facets go forward
                       in time.  When false the go back in time.

        :param from_date: Defaults to today.
        """

        today = from_date or datetime.date.today()
        format = lambda d: d.strftime("%Y%m%d")
        last_day = lambda y, m: 29 if \
                   (calendar.isleap(y) and m == 2) else calendar.mdays[m]
        ranges = []
        if future:
            deltas = (('today', 0, 0), ('tomorrow', 1, 1), ('this week', 2, 7))
            months = xrange(months)
        else:
            deltas = (('today', 0, 0),
                      ('yesterday', -1, -1),
                      ('past week', -2, -7))
            months = xrange(0, -months, -1)
        for d in deltas:
            ranges.append((
                format(today + datetime.timedelta(d[1])),
                format(today + datetime.timedelta(d[2])),
                d[0],
            ))
        for n in months:
            mm = (today.month - 1 + n)
            month = (mm % 12) + 1
            year = mm / 12 + today.year
            ranges.append((
                format(datetime.date(year, month, 1)),
                format(datetime.date(year, month, last_day(year, month))),
                "%s %d" % (calendar.month_name[month], year),
            ))
        for range in ranges[:]:
            if valname:
                values = self.values[valname]
                for value in values:
                    if value >= range[0] and value <= range[1]:
                        break
                else:
                    ranges.remove(range)
        return ranges
