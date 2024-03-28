# -*- coding: utf-8 -*-
# @Author: wqshen
# @Email: wqshen91@gmail.com
# @Date: 2021/5/31 15:47
# @Last Modified by: wqshen

import pytest
import pandas as pd
from datetime import datetime, timedelta
from pydaas.client import DaasClient

pd.set_option('display.width', None)
pd.set_option('display.max_columns', None)
pd.set_option('max_colwidth', 1000)


class TestDaas:
    dc = DaasClient(user='xxx', password='xxx')
    inittime = datetime.utcnow().replace(minute=0, second=0, microsecond=0, hour=12) - timedelta(days=2)

    def test_ecmwf_high_element_inrect(self):
        """测试指定经纬度范围读取ECMWF高空变量"""
        dar = self.dc.sel('ECMWF_P', self.inittime, fh=24, varname='RHU', level=850,
                          lat=slice(20, 40), lon=slice(110, 130))
        print(dar)

    def test_ecmwf_high_element_atpoint(self):
        """测试指定经纬度点读取ECMWF高空变量"""
        dar = self.dc.sel('ECMWF_P', self.inittime, fh=24, varname='RHU', level=850,
                          lat=[30,35], lon=[120,122])
        print(dar)

    def test_ecmwf_high_element_atpoint_timeseries(self):
        """测试指定经纬度点读取ECMWF高空变量预报时间序列"""
        dar = self.dc.sel('ECMWF_P', self.inittime, fh=slice(0, 72), varname='RHU', level=850,
                          lat=30, lon=120)
        print(dar)

    def test_ecmwf_eps_surface_element_inrect(self):
        """测试指定经纬度范围读取ECMWF集合预报高空变量"""
        inittime = datetime(2023, 6, 4, 0)
        dar = self.dc.sel('NAFP_C3E_FOR_FTM_LOW_ASI', inittime, fh=24, varname='TEM',
                          lat=slice(20, 40), lon=slice(110, 130), )
        print(dar)

    def test_grapes_surface_element_inrect(self):
        """测试指定经纬度范围读取ECMWF集合预报高空变量"""
        dar = self.dc.sel('GRAPES_GFS', datetime(2023, 6, 5, 0), fh=24, varname='TPE',
                          lat=slice(20, 40), lon=slice(110, 130))
        print(dar)

    def test_grapes_3km_surface_element_inrect(self):
        """测试指定经纬度范围读取ECMWF集合预报高空变量"""
        dar = self.dc.sel('CMA_SH3', datetime(2023, 6, 5, 0), fh=24, varname='TPE',
                          lat=slice(20, 40), lon=slice(110, 130), download='/data')
        print(dar)

    def test_surface_hourly(self):
        """读取地面小时观测数据"""
        variable = 'Station_Id_C,Station_Name,Lon,Lat,Alti,Datetime,PRE_1H'
        dar = self.dc.sel('SURFACE', slice(self.inittime - timedelta(days=30), self.inittime), varname=variable,
                          index_col='Station_Id_C', staIds='58457',
                          orderBy='Datetime:desc')  # lon=slice(110, 130), lat=slice(20, 40), )
        print(dar)

    def test_stat_surface_hour(self):
        variable = 'SUM_PRE_1H'
        dar = self.dc.sel('SURFACE', slice(self.inittime - timedelta(days=1), self.inittime),
                          varname=variable,
                          index_col='Station_Id_C,Station_Name,Lon,Lat,Alti',
                          lon=slice(110, 130), lat=slice(20, 40),
                          orderBy='Station_Id_C:asc')
        print(dar)

    def test_stat_surface_hour_region(self):
        variable = 'SUM_PRE_1H'
        dar = self.dc.sel('SURFACE', slice(self.inittime - timedelta(days=1), self.inittime),
                          varname=variable,
                          index_col='Station_Id_C,Station_Name,Lon,Lat,Alti',
                          adminCodes='330000',
                          orderBy='Station_Id_C:asc')
        print(dar)

    def test_typhoon(self):
        variable = 'Datetime,TYPH_Name,V_CHN_NAME,Num_Nati,Bul_Center,Lat,Lon,PRS,Validtime'
        inittime = datetime(2023, 7, 29, 12)
        dar = self.dc.sel('SEVP_ZJ_WEFC_TYP_WT', slice(inittime - timedelta(days=1), inittime),
                          varname=variable,
                          reportCenters='BABJ',
                          typhNames='DOKSURI',
                          orderBy='Num_Nati:asc,Bul_Center:asc,Validtime:asc,Datetime:asc'
                          )
        print(dar)

    def test_cmpas(self):
        # CMPA test failed, Daas internal problem
        dar = self.dc.sel('CMPA_HOR', datetime(2023, 6, 5, 0), varname='PRE',
                          lat=slice(20, 40), lon=slice(110, 130))
        print(dar)

    def test_cldas_d(self):
        dar = self.dc.sel('CLDAS_D', datetime(2023, 6, 14, 8), fh=None,
                          varname='MNT',
                          level=None, )
        print(dar)

    def test_surface_hourly_inrect(self):
        """读取指定经纬度范围内的地面小时观测数据"""
        variable = 'Station_Id_C,Station_Name,Lon,Lat,Alti,Datetime,PRE_1H'
        dar = self.dc.sel('SURFACE', slice(self.inittime - timedelta(days=30), self.inittime), varname=variable,
                          index_col='Station_Id_C', lon=slice(110, 130), lat=slice(20, 40),
                          orderBy='Datetime:desc,Station_Id_C:asc')
        print(dar)

    def test_surface_daily(self):
        """读取地面日观测数据"""
        variable = 'Station_Id_C,Station_Name,Lon,Lat,Alti,Datetime,PRE_Time_0808'
        self.inittime = datetime(2023, 6, 13, 20)
        dar = self.dc.sel('SURF_CHN_MUL_DAY', slice(self.inittime - timedelta(days=30), self.inittime),
                          varname=variable,
                          index_col='Station_Id_C', staIds='58457',
                          orderBy='Datetime:desc', )  # lon=slice(110, 130), lat=slice(20, 40), )
        print(dar)

    def test_lighting_cn(self):
        variable = 'Datetime,Lat,Lon,Lit_Current,Alti,V73001'
        self.inittime = datetime(2024, 3, 25, 9)
        dar = self.dc.sel('UPAR_ADTD_CHN_LIS', slice(self.inittime - timedelta(hours=3), self.inittime),
                          varname=variable,
                          index_col='Datetime',
                          orderBy='Datetime:desc', lon=slice(117, 124), lat=slice(26, 32), )
        print(dar)

    def test_lighting_zj(self):
        variable = 'Datetime,Lat,Lon,Lit_Current,Pois_Err,HEIGHT'
        self.inittime = datetime(2024, 3, 25, 9)
        dar = self.dc.sel('UPAR_THUNDER_ZJ_TAB', slice(self.inittime - timedelta(hours=1), self.inittime),
                          varname=variable,
                          index_col='Datetime',
                          orderBy='Datetime:desc')
        print(dar)


if __name__ == '__main__':
    pytest.main(['-q', 'test_diamond_reader.py'])
