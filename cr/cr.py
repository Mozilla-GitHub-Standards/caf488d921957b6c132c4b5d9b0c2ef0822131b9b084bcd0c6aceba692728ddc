#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

class ChangeRequest(object):
    def __init__(self):
        pass

    def execute(self, command, **kwargs):
        return {
            'create': self.create,
            'show': self.show,
        }[command](**kwargs)

    def create(self,
        planned_start_date=None,
        planned_end_date=None,
        change_plan=None,
        short_description=None,
        business_impact=None,
        change_impact=None,
        user_impact=None,
        security_risk_level=None,
        change_frequency=None,
        test_plan=None,
        post_implementation_plan=None,
        customer_end_user_plan=None,
        rollback_procedure=None,
        peer_review_date=None,
        vendor_name=None,
        planned_downtime=None,
        verbose=False,
        **kwargs):
        from pprint import pprint
        pprint(locals())

    def show(self, **kwargs):
        pass
