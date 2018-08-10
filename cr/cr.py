#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cr.utils.json import print_json

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
        template_name=None,
        verbose=False,
        **kwargs):
        print_json(locals(), 'self', 'verbose', 'kwargs')

    def show(self, **kwargs):
        pass
