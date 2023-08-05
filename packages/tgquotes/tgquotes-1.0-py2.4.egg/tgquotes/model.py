from sqlobject import *

from turbogears.database import PackageHub

import random

hub = PackageHub("tgquotes")
__connection__ = hub

class Quote(SQLObject):
    quote = UnicodeCol(notNone=True)

    @classmethod
    def random(cls,num=1):
        """
        Returns $num quotes, selected at random, or all of the quotes if num is larger.
        """
        if num > Quote.select().count():
            return list(Quote.select())
        else:
            return random.sample(list(Quote.select()),num)

# class YourDataClass(SQLObject):
#     pass

