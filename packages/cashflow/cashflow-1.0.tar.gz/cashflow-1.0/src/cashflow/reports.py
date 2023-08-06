"""Various reports that can be generated from a GnuCash ledger book."""

from collections import defaultdict

def make_int_dict():
    """A dictionary whose default values are (integer) zero."""
    return defaultdict(int)

def sorted_rows(rows):
    """Return the sequence of rows, sorted by the 4th column."""
    def fourth_tuple_item(t):
        return t[3]
    return sorted(rows, key=fourth_tuple_item)

def cashflow(book, one_month=None, cash_types=('BANK', 'CASH', 'CREDIT'),
             account_map={}, is_cash=[], isnt_cash=[], regular_expenses=[]):
    """Print a cash flow report for the given month, or all months."""
    month_regular = defaultdict(make_int_dict)
    month_expenses = defaultdict(make_int_dict)
    month_income = defaultdict(make_int_dict)

    # Fetch the accounts from inside this GnuCash ledger book.

    account_list = [ a for a in book.accounts ]

    # First, determine by what name each account should be known, and
    # create a map from account guids (which are what we will find named
    # in transaction splits) to printable account names; we include any
    # transforms specified in our account_map parameter.  This might
    # result in several accounts being mapped to the same name.

    account_names = {}
    for account in account_list:
        name = account.name
        while name in account_map:
            name = account_map[name]
        account_names[account.guid] = name

    # Next, we need to determine which accounts count as our cash pool.

    accounts = dict( (a.guid, a) for a in account_list )
    cash_account_guids = set( a.guid for a in account_list
                              if a.type in cash_types)
    for name in is_cash:
        aa = [ a for a in account_list if a.name == name ]
        if not aa:
            raise ValueError('no account has the name %r' % name)
        if len(aa) > 1:
            raise ValueError('%d accounts have the name %r' % (len(aa), name))
        cash_account_guids.add(aa[0].guid)

    for name in isnt_cash:
        aa = [ a for a in account_list if a.name == name ]
        if not aa:
            raise ValueError('no account has the name %r' % name)
        if len(aa) > 1:
            raise ValueError('%d accounts have the name %r' % (len(aa), name))
        #print '---------', cash_account_guids
        cash_account_guids.remove(aa[0].guid)
        #print '---------', cash_account_guids

    for t in book.transactions:
        #print t.date_posted
        month = t.date_posted[:7] # string like '2008-08'
        #print month
        splits = list(t.splits)
        if any( (s.account_guid in cash_account_guids) for s in splits ):
            for split in splits:
                guid = split.account_guid
                if guid not in cash_account_guids:
                    name = account_names[guid]
                    value = split.value
                    ivalue = int(value[:value.find('/')])
                    if ivalue > 0:
                        if name in regular_expenses:
                            month_regular[month][name] -= ivalue
                        else:
                            month_expenses[month][name] -= ivalue
                    elif ivalue < 0:
                        month_income[month][name] -= ivalue

    rows = []

    months = set()
    months.update(month_expenses)
    months.update(month_income)
    months = sorted(months)

    t = 0
    for month in months:
        if one_month is None or month == one_month:
            t2 = 0

            if month_income[month]:
                rows.append(())
                t3 = 0
                for name, total in sorted(month_income[month].items()):
                    rows.append((None, None, total, name))
                    t3 += total
                rows.append((None, None, '-'))
                rows.append((None, t3, t3, 'Income for ' + month))
                t2 += t3

            if month_regular[month]:
                rows.append(())
                t3 = 0
                for name, total in sorted(month_regular[month].items()):
                    rows.append((None, None, total, name))
                    t3 += total
                rows.append((None, None, '-'))
                rows.append((None, t3, t3, 'Regular expenses for ' + month))
                t2 += t3

            if month_expenses[month]:
                rows.append(())
                t3 = 0
                for name, total in sorted(month_expenses[month].items()):
                    rows.append((None, None, total, name))
                    t3 += total
                rows.append((None, None, '-'))
                rows.append((None, t3, t3, 'Expenses for ' + month))
                t2 += t3

            rows.append((None, '-'))
            rows.append((t2, t2, '', 'Monthly total for ' + month))
            t += t2
            rows.append(('-'))
            rows.append((t, '', '', 'Running total after ' + month))

    return rows
