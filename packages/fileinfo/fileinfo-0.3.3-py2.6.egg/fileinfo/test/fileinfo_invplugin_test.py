#!/usr/bin/env python
# _*_ coding: UTF-8 _*_

"""Contains a test investigator.

"""

from fileinfo.investigator import BaseInvestigator


class TestInvestigator(BaseInvestigator):
    "A class for determining attributes of files."

    attrMap = {
        "foo": "getFoo",
    }

    totals = ()

    def activate(self):
        "Try activating self, setting 'active' variable."

        self.active = True
        return self.active


    def getFoo(self):
        "Return 'bar'."

        return "bar" 