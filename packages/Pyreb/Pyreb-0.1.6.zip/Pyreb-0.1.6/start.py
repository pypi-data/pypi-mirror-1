#!/usr/bin/python
import Pyreb
try:
    import psyco
    psyco.log('psyco.log')
    psyco.profile()
except:
    print 'Psyco not found, ignoring it'

Pyreb.main()
