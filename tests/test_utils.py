import pytest

import f3tch.utils as utils

def test_shorten_metric_name():
    metric_name = "foo-bar-foo"
    max_len = 20
    
    actual = utils.shorten_metric_name(metric_name,max_len)
    expected = "foo-bar-foo"
    assert actual == expected

    max_len = 10
    actual = utils.shorten_metric_name(metric_name,max_len)
    expected = "foo-bar-fo_capped"
    assert actual == expected

def test_strtime_to_timestamp():
    strtime = "18.05.2022 16:08:05"

    actual = utils.strtime_to_timestamp(strtime)
    expected = 1652904485

    assert actual == expected

def test_convert_time():
    timestamp = 1652904485

    actual = utils.convert_time(timestamp)
    expected = "2022-05-18 16:08:05"

    assert actual == expected