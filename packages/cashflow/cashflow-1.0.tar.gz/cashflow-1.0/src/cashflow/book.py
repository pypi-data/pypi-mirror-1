"""Models that represent GnuCash data.

These classes are lightweight wrappers around the actual ElementTree
that holds the data from inside a GnuCash save file.  Typically the user
simply needs to parse the file and instantiate a Book() around its tree
object; a convenience function for doing this is defined at the top of
this package.

"""
from cashflow.oxm import XMLWrapper, XMLChild, XMLChildText, XMLChildren

# Precompute the names of common GnuCash XML tags.

def tag(colontag):
    """Return the fully-qualified XML tag name for a GnuCash tag."""
    prefix, name = colontag.split(':')
    return '{http://www.gnucash.org/XML/%s}%s' % (prefix, name)

gnc_book = tag('gnc:book')
gnc_account = tag('gnc:account')
gnc_transaction = tag('gnc:transaction')
act_id = tag('act:id')
act_name = tag('act:name')
act_type = tag('act:type')
trn_date_posted = tag('trn:date-posted')
trn_splits = tag('trn:splits')
trn_split = tag('trn:split')
ts_date = tag('ts:date')
split_value = tag('split:value')
split_account = tag('split:account')

# The actual classes used to expose a GnuCash file.

class Split(XMLWrapper):
    """A GnuCash split (one of several parts of a transaction)."""
    value = XMLChildText(split_value)
    account_guid = XMLChildText(split_account)

class Splits(XMLWrapper):
    """A GnuCash splits element."""
    splits = XMLChildren(trn_split, Split)

    def __iter__(self):
        return self.splits

class Transaction(XMLWrapper):
    """A GnuCash transaction."""
    date_posted = XMLChildText(trn_date_posted, ts_date)
    splits = XMLChild(trn_splits, Splits)

class Account(XMLWrapper):
    """A GnuCash account."""
    guid = XMLChildText(act_id)
    name = XMLChildText(act_name)
    type = XMLChildText(act_type)

class Book(object):
    """A GnuCash ledger book (the contents of a GnuCash save file)."""

    def __init__(self, tree):
        # init method saves the tree object, to support write() someday
        self.tree = tree
        self.element = tree.find(tag('gnc:book'))

    accounts = XMLChildren(gnc_account, Account)
    transactions = XMLChildren(gnc_transaction, Transaction)
