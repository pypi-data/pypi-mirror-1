The ``cashflow`` package
========================

This package provides a `cashflow` script that can easily be invoked
from the command line, as well as useful modules that you can use in
your own programs that want to manipulate Gnucash data.  It is designed
to operate on Gnucash save files (though not very flexibly, yet; it
assumes a base-ten currency, for example) and to determine where your
money is going each month.

The idea is that it reads through your Gnucash ledger, and for each
month creates a tally of which accounts have provided income, which
accounts have absorbed expenses, and therefore whether you finished the
month with more or less cash than when you started it.  A running total
is kept from month to month indicating whether your cash reserves are
increasing or depleting.  If the amount is slowly growing, then you
might think about investing or spending the surplus; if, instead, your
cash-on-hand is inexorably decreasing, then you might be on the way to
bankruptcy.

You can install this package with `easy_install`, and then simply run
the resulting command like::

 $ cashflow ledger.gnucash

You can also ask for the same report to be generated from Python,
which requires a few more lines of effort.  Here is what the report
looks like for a small two-month ledger included with the `cashflow`
module as a sample:

>>> import cashflow
>>> book = cashflow.open(cashflow.sample_file_path())

>>> from cashflow.format import display
>>> from cashflow.reports import cashflow
>>> display(cashflow(book))
<BLANKLINE>
                           1.17   Interest
                       2,821.00   Salary
                       ---------
            2,822.17   2,822.17   Income for 1980-01
<BLANKLINE>
                        (125.63)  Groceries
                         (41.18)  Utilities
                       ---------
             (166.81)   (166.81)  Expenses for 1980-01
            ---------
 2,655.36   2,655.36              Monthly total for 1980-01
 ---------
 2,655.36                         Running total after 1980-01
<BLANKLINE>
                           2.30   Interest
                       2,821.00   Salary
                       ---------
            2,823.30   2,823.30   Income for 1980-02
<BLANKLINE>
                        (130.93)  Groceries
                         (48.62)  Utilities
                       ---------
             (179.55)   (179.55)  Expenses for 1980-02
            ---------
 2,643.75   2,643.75              Monthly total for 1980-02
 ---------
 5,299.11                         Running total after 1980-02
