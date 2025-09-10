# resources.py
from import_export import resources
from .models import OysterFarmingStats


class OysterFarmingStatsResource(resources.ModelResource):
    class Meta:
        model = OysterFarmingStats
        fields = (
            "id",
            "year",
            "horizontal_facilities_nation",
            "horizontal_farmers_nation",
            "horizontal_facilities_changhua",
            "horizontal_farmers_changhua",
            "horizontal_facilities_fangyuan",
            "horizontal_farmers_fangyuan",
            "stake_facilities_nation",
            "stake_farmers_nation",
            "stake_facilities_changhua",
            "stake_farmers_changhua",
            "stake_facilities_fangyuan",
            "stake_farmers_fangyuan",
            "hanging_facilities_nation",
            "hanging_farmers_nation",
            "hanging_facilities_changhua",
            "hanging_farmers_changhua",
            "hanging_facilities_fangyuan",
            "hanging_farmers_fangyuan",
            "raft_facilities_nation",
            "raft_farmers_nation",
            "raft_facilities_changhua",
            "raft_farmers_changhua",
            "raft_facilities_fangyuan",
            "raft_farmers_fangyuan",
            "longline_facilities_nation",
            "longline_farmers_nation",
            "longline_facilities_changhua",
            "longline_farmers_changhua",
            "longline_facilities_fangyuan",
            "longline_farmers_fangyuan",
            "total_farmers_nation",
            "total_farmers_changhua",
            "total_farmers_fangyuan",
        )
        export_order = fields
