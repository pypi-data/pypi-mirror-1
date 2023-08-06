"""
South introspection rules.
"""

import django
from django.conf import settings

from south.modelsinspector import add_introspection_rules

has_sf_utils = "softwarefabrica.django.utils" in settings.INSTALLED_APPS

if has_sf_utils:
    try:
        from softwarefabrica.django.utils.UUIDField import UUIDField
    except ImportError:
        pass
    else:
        rules = [
            (
                (UUIDField, ),
                [],
                {
                    "auto": ["auto", {"default": True}],
                    "version": ["version", {"default": 1}],
                    "node": ["node", {"default": None}],
                    "clock_seq": ["clock_seq", {"default": None}],
                    "namespace": ["namespace", {"default": None}],
                    "max_length": ["max_length", {"default": 36}],
                    "blank": ["blank", {"default": False, "ignore_if": 'auto'}],
                    "editable": ["editable", {"default": False}],
                },
            ),
        ]

    add_introspection_rules(rules, ["^softwarefabrica\.django\.utils",])

    try:
        from softwarefabrica.django.utils.IPv4MaskedAddressField import IPv4MaskedAddressField
    except ImportError:
        pass
    else:
        rules = [
            (
                (IPv4MaskedAddressField, ),
                [],
                {
                    "max_length": ["max_length", {"default": 48}],
                },
            ),
        ]

    add_introspection_rules(rules, ["^softwarefabrica\.django\.utils",])
