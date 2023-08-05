import MySQLdb
import datetime
import math

# special quote/escape chracters (if any)
quote_chars = ["`"]
escape_chars = ['\\']

def init1(wrapper):
    # MySQLDb does not define DATETIME
    wrapper._driver.DATETIME = wrapper._driver.DBAPISet(10, 12)

# convertdt not needed b/c it used mx.DateTime
