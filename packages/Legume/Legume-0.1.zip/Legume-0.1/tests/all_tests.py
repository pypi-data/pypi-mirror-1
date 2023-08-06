# legume. Copyright 2009 Dale Reidy. All rights reserved. See LICENSE for details.

import unittest
from greenbar import GreenBarRunner
import test_udp
import test_keepalive
import test_events

if __name__ == '__main__':
    suite_udp = unittest.TestLoader().loadTestsFromModule(test_udp)
    suite_keepalive = unittest.TestLoader().loadTestsFromModule(test_keepalive)
    suite_events = unittest.TestLoader().loadTestsFromModule(test_events)

    all_suites = unittest.TestSuite()
    all_suites.addTests([suite_udp, suite_keepalive, suite_events])
    GreenBarRunner(verbosity=2).run(all_suites)