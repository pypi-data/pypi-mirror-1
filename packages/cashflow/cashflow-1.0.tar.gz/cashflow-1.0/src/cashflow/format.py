"""Format text for output in columns on the screen."""

from collections import defaultdict

def format_money(n):
    """Ledger-format dollar amounts, producing strings like '(5,138.22)'."""
    s = '%d.%02d' % divmod(abs(n), 100)
    for i in range(-6, -len(s), -3):
        s = s[:i] + ',' + s[i:] # put in thousands commas
    if n < 0:
        return '(%s)' % s
    else:
        return '%s ' % s # trailing space keeps numbers aligned

class Table(object):
    """Accept a list of rows, and print them with aligned columns."""

    def __init__(self):
        self.lines = []
        self.fieldwidths = defaultdict(int)

    def append(self, args):
        """Add a new row of fields, given as zero or more arguments."""
        # We also update our record of how wide each column needs to be.
        fields = []
        fieldwidths = self.fieldwidths
        for i, field in enumerate(args):
            if isinstance(field, int):
                field = format_money(field)
            elif field is None:
                field = ''
            fieldwidths[i] = max(fieldwidths[i], len(field))
            fields.append(field)
        self.lines.append(fields)

    def display(self):
        """Print out all of the rows of data we were given."""
        fieldwidths = self.fieldwidths
        lastfield = len(fieldwidths) - 1
        for line in self.lines:
            for i, field in enumerate(line):
                if field == '-':
                    print ' ' + '-' * fieldwidths[i],
                elif i < lastfield:
                    print ' %*s' % (fieldwidths[i], field or ''),
                else:
                    print ' ' + (field or ''),
            print

def display(rows):
    """Given a sequence of rows, print them as a table."""
    t = Table()
    for row in rows:
        t.append(row)
    t.display()
