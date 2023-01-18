"""
    Tests for the capacity check library
"""
from arise_prototype import capacity_check as cc
from pandas.testing import assert_frame_equal
import pandas as pd


def test_machine_parser():
    data = {'MaschNr': ['SL 1', 'SL 12 Rota', 'Handwerkzeug'],
            'Order': [4, 2, 3]}
    df = pd.DataFrame(data)
    df1 = cc.parse_machine_number(df)
    data2 = {'MaschNr': ['SL 1', 'SL 12 Rota'],
             'Order': [4, 2],
             'machine': ['SL 1', 'SL 12'],
             'machine_id': ['1', '12']}
    df2 = pd.DataFrame(data2)
    print('Tests machine parser')
    assert_frame_equal(df1, df2)


def test_material_check():
    test_date1 = pd.to_datetime("2016-02-16").date()
    test_date2 = pd.to_datetime("2016-02-18").date()
    material_check_test = cc.material_check(test_date1)
    assert not material_check_test(test_date2)
