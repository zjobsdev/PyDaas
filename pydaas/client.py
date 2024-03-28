# -*- coding: utf-8 -*-
# @Author: wqshen
# @Email: wqshen91@gmail.com
# @Date: 2023/2/6 10:23
# @Last Modified by: wqshen

import os
import yaml
import numpy as np
import configparser
import pandas as pd
import xarray as xr
from typing import Union
from logzero import logger
from itertools import product
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from pydaas.music.DataQueryClient import DataQueryClient


class DaasClient(DataQueryClient):
    def __init__(self, user: str = None, password: str = None, **kwargs):
        """Daas

        Parameters
        ----------
        user: str
            user name
        password: str
            password
        kwargs:
            other parameters passed into DataQueryClient
        """
        conf_dir = fr'{os.path.dirname(__file__)}/config'
        default_config = fr'{conf_dir}/client.config'
        kwargs['config_file'] = kwargs.get('config_file', default_config)
        logger.debug(f"load client.config from {kwargs['config_file']}")
        super().__init__(**kwargs)

        cf = configparser.ConfigParser()
        cf.read(kwargs['config_file'], 'utf-8')
        self._user = cf.get('Pb', 'music_user') if user is None else user
        self._password = cf.get('Pb', 'music_password') if password is None else password
        self._n_jobs = 1
        self.alias = self.load_yaml(fr'{conf_dir}/alias.yaml')

    @property
    def n_jobs(self) -> int:
        """getter attribute for thread numbers"""
        return self._n_jobs

    @n_jobs.setter
    def n_jobs(self, n: int):
        """setter thread numbers in parallel get data

        Parameters
        ----------
        n : int
            thread number in parallel get data
        """
        self._n_jobs = n

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        del self

    @staticmethod
    def load_yaml(path_yaml: str, encoding: str = 'utf8') -> dict:
        """load yaml configuration file

        Parameters
        ----------
        path_yaml: str
            path to yaml file
        encoding: str
            file encoding, default 'utf8'

        Returns
        -------
        res: dict
            A dict like object
        """
        if not os.path.isfile(path_yaml):
            raise FileNotFoundError(path_yaml)

        with open(path_yaml, "r", encoding=encoding) as f:
            return yaml.safe_load(f)

    @property
    def user(self) -> str:
        """get property user"""
        return self._user

    @user.setter
    def user(self, user: str):
        """set property user"""
        self._user = user

    @property
    def password(self) -> str:
        """get property password"""
        return self._password

    @password.setter
    def password(self, pwd: str):
        """set property password"""
        self._password = pwd

    def sel(self, datasource: Union[str, list], inittime: Union[datetime, slice, list, str] = None,
            fh: Union[int, slice, list] = None, varname: Union[str, list] = None,
            leadtime: Union[datetime, slice, list, str] = None,
            merge: bool = False,
            **kwargs) -> Union[xr.DataArray, pd.DataFrame, list]:
        """interface to select variable from file by given more filter and clip parameters

        Parameters
        ----------
        datasource (str, list): data source name from Daas, also alias from config/alias.yaml
        inittime (datetime, slice, list): model initial datetime or observation time
        fh (int, list): forecast hour
        varname (str, list): variable name
        kwargs (dict): other k/v arguments passed to `sel` method of specific reader

        Returns
        -------
        (pd.DataFrame, xarray.DataArray, list[xarray.DataArray]): Readed variable
        """
        datasource = [datasource] if isinstance(datasource, str) else datasource
        datasource = [self.alias.get(d, d) for d in datasource]
        inittime = [inittime] if isinstance(inittime, (datetime, slice, str)) or inittime is None else inittime
        leadtime = [leadtime] if isinstance(leadtime, (datetime, slice, str)) or leadtime is None else leadtime
        fh = [fh] if isinstance(fh, (int, slice, str)) or fh is None else fh
        varname = [varname] if isinstance(varname, str) or varname is None else varname
        requests = list(product(datasource, inittime, fh, varname, leadtime))

        with ThreadPoolExecutor(max_workers=self._n_jobs) as executor:
            datas = list(executor.map(lambda r: self._sel(r, **kwargs), requests))
            if all([i is None for i in datas]):
                logger.exception(f"all requests failed.")
                raise Exception(f"all requests failed.")
            if merge:
                if isinstance(datas, list):
                    if isinstance(datas[0], (xr.DataArray, xr.Dataset)):
                        if len(inittime) > 1 and all([d.time == datas[0].time for d in datas]):
                            leadtime = xr.DataArray(datas[0].time.values, dims='time')
                            datas = [d.set_index(time='inittime').assign_coords(leadtime=leadtime) for d in datas]
                        datas = xr.merge(datas)
                    elif isinstance(datas[0], pd.DataFrame):
                        datas = pd.concat(datas)
                elif isinstance(datas, xr.DataArray):
                    datas = datas.to_datas()
                elif isinstance(datas, (list, xr.Dataset, pd.DataFrame, pd.Series)):
                    pass
                else:
                    raise NotImplementedError(datas)
                return datas
            return datas if len(requests) > 1 else datas[0]

    def _sel(self, request: Union[list, tuple], **kwargs):
        logger.debug(request)
        request = dict(zip(('datasource', 'inittime', 'fh', 'varname', 'leadtime'), request))
        request['inittime'], request['fh'] = self.decode_leadtime(request['inittime'], request['fh'],
                                                                  request['leadtime'])

        logger.debug(request)
        interface_method = getattr(self, f"_sel_{request['datasource'].split('_')[0].lower()}")

        try:
            return interface_method(**request, **kwargs)
        except Exception as e:
            logger.exception("{} - {}".format(request, e))
            return

    def decode_leadtime(self, inittime=None, fh=None, leadtime=None):
        """Decode inittime, fh and leadtime

        Parameters
        ----------
        inittime (datetime): intial datetime
        fh (int): other k/v arguments passed to `sel` method of specific reader
        leadtime (datetime): kwargs passed to wcard construction

        Returns
        -------
        (xarray.DataArray, list[xarray.DataArray]): Readed variable in xarray.DataArray
        """
        assert inittime is not None or leadtime is not None

        if fh is None:
            if leadtime is not None and inittime is not None:
                fh = int((leadtime - inittime).total_seconds() / 3600.)

        if inittime is None:
            inittime = leadtime - timedelta(hours=fh)

        return inittime, fh

    def _sel_file(self, datasource: str, inittime: Union[datetime, slice] = None, **kwargs):
        """sel nafp (model) file from daas

        Parameters
        ----------
        datasource: str
            data source name from Daas
        inittime: datetime, slice
            model initial datetime
        kwargs:
            other parameters, not implemented

        Returns
        -------
        ret:
            a list of url or download directly based on default call method
        """
        default_call = "callAPI_to_downFile"
        # default_call = "callAPI_to_fileList"
        parameters = {
            "dataCode": self.alias.get(datasource, datasource),
        }
        dtype = datasource.split('_')[0].capitalize()
        interface = f'get{dtype}File'

        if isinstance(inittime, slice):
            interface += 'ByTimeRange'
            parameters.update({"timeRange": f"[{inittime.start:%Y%m%d%H%M%S},{inittime.stop:%Y%m%d%H%M%S}]"})
        else:
            interface += 'ByTime'
            parameters.update({"time": f"{inittime:%Y%m%d%H%M%S}"})
        if kwargs.get('staIds'):
            interface += 'AndStaID'
            parameters.update({"staIds": kwargs.get('staIds')})

        path = kwargs.pop('path', './')
        ret = getattr(self, default_call)(self._user, self._password, interface, parameters, path)
        return ret.fileInfos

    def _sel_nafp(self, datasource: str, inittime: Union[datetime, slice] = None,
                  fh: Union[int, slice] = None, varname: str = None,
                  **kwargs) -> Union[pd.DataFrame, xr.DataArray]:
        """Sel  nafp (model) variable from daas

        Parameters
        ----------
        datasource: str
            data source name from Daas
        inittime: datetime, slice
            model initial datetime
        fh: int, slice
            forecast lead hours
        varname: str
            forecast variable name
        kwargs:
            lat,lon: slice or point

        Returns
        -------
        (xr.DataArray, pd.DataFrame): variable
        """
        download = kwargs.pop('download', False)
        if download:
            url = self._sel_file(datasource, inittime, path=download, **kwargs)
            return url

        default_call = "callAPI_to_gridArray2D"
        level = kwargs.pop('level', 0)
        if 'levelType' in kwargs:
            level_type = kwargs.get('levelType')
        else:
            level_type = 1 if level == 0 else 100
        parameters = {
            "dataCode": self.alias.get(datasource, datasource),
            "time": f"{inittime:%Y%m%d%H%M%S}",
            "fcstEle": varname,

        }
        if level is None:
            parameters.update({"levelType": "-"})
        else:
            parameters.update({"levelType": f"{kwargs.pop('levelType', level_type)}",
                               "fcstLevel": f"{kwargs.pop('level', level)}", })

        interface = "getNafpEle"
        if datasource.startswith('NAFP_GRID_ANA'):
            interface = "getNafpAnaEle"

        if kwargs.get('lat') and kwargs.get('lon'):
            lat, lon = kwargs.get('lat'), kwargs.get('lon')

            if isinstance(lat, slice):
                interface += 'GridInRect'
                parameters.update(
                    {'minLat': f"{lat.start}",
                     'maxLat': f"{lat.stop}",
                     'minLon': f"{lon.start}",
                     'maxLon': f"{lon.stop}"}
                )
            else:
                interface += 'AtPoint'
                if isinstance(lat, (list, tuple)) and isinstance(lon, (list, tuple)):
                    points = ','.join([f'{y}/{x}' for y, x in zip(lat, lon)])
                else:
                    points = f'{lat}/{lon}'
                parameters.update({'latLons': points})
                default_call = "callAPI_to_array2D"
        else:
            interface += 'Grid'
        interface += 'ByTimeAndLevel'

        time = inittime
        if isinstance(fh, slice):
            interface += 'AndValidtimeRange'
            parameters.update(
                {'minVT': f"{fh.start}",
                 'maxVT': f"{fh.stop}"}
            )
        elif fh is not None:
            interface += 'AndValidtime'
            parameters.update({'validTime': f"{fh}"})
            time = inittime + timedelta(hours=fh)

        ret = getattr(self, default_call)(self._user, self._password, interface, parameters)
        if ret.request.errorCode == 0:
            logger.debug(ret)
            if default_call == "callAPI_to_array2D":
                # TODO: 返回不一致的数据类型，让人不知所措
                data = pd.DataFrame(ret.data, columns=list(ret.elementNames))
            else:
                if datasource == "NAFP_C3E_FOR_FTM_LOW_ASI":
                    rets = [ret.data]
                    for i in range(1, 51):
                        parameters['fcstLevel'] = f"{i}"
                        ret = getattr(self, default_call)(self._user, self._password, interface, parameters)
                        rets.append(ret.data)
                    data = xr.DataArray([rets], dims=('time', 'number', 'lat', 'lon'),
                                        coords={'time': [time],
                                                # 'inittime': [inittime],
                                                'number': np.arange(51, dtype='i4'),
                                                'lon': np.linspace(ret.startLon, ret.endLon, ret.lonCount),
                                                'lat': np.linspace(ret.startLat, ret.endLat, ret.latCount)},
                                        name=varname)
                    data = data.assign_coords(inittime=xr.DataArray([inittime], dims='time'))
                else:
                    data = xr.DataArray([ret.data], dims=('time', 'lat', 'lon'),
                                        coords={'lon': np.linspace(ret.startLon, ret.endLon, ret.lonCount),
                                                'lat': np.linspace(ret.startLat, ret.endLat, ret.latCount),
                                                # 'inittime': [inittime],
                                                'time': [time]},
                                        name=varname)
                    data = data.assign_coords(inittime=xr.DataArray([inittime], dims='time'))

            return data
        else:
            logger.debug(ret.request)
            raise Exception(ret.request.errorCode, ret.request.errorMessage)

    def _sel_surf_grid(self, datasource: str, inittime: Union[datetime, slice] = None,
                       varname: str = None, **kwargs) -> Union[pd.DataFrame, xr.DataArray]:
        """Sel surface (observation) grid variable from daas

        Parameters
        ----------
        datasource: str
            data source name from Daas
        inittime: datetime, slice
            observation datetime
        varname: str
            observation variable name
        kwargs:
            lat,lon: slice or point

        Returns
        -------
        (xr.DataArray, pd.DataFrame): variable
        """
        default_call = "callAPI_to_gridArray2D"
        parameters = {"dataCode": self.alias.get(datasource, datasource),
                      "time": f"{inittime:%Y%m%d%H%M%S}",
                      "fcstEle": varname, }

        interface = "getSurfEle"
        if kwargs.get('lat') and kwargs.get('lon'):
            lat, lon = kwargs.get('lat'), kwargs.get('lon')

            if isinstance(lat, slice):
                interface += 'GridInRect'
                parameters.update(
                    {'minLat': f"{lat.start}",
                     'maxLat': f"{lat.stop}",
                     'minLon': f"{lon.start}",
                     'maxLon': f"{lon.stop}"}
                )
            else:
                interface += 'AtPoint'
                if isinstance(lat, (list, tuple)) and isinstance(lon, (list, tuple)):
                    points = ','.join([f'{y}/{x}' for y, x in zip(lat, lon)])
                else:
                    points = f'{lat}/{lon}'
                parameters.update({'latLons': points})
                default_call = "callAPI_to_array2D"
        else:
            interface += 'Grid'
        interface += 'ByTime'
        ret = getattr(self, default_call)(self._user, self._password, interface, parameters)
        if ret.request.errorCode == 0:
            logger.debug(ret)
            if default_call == "callAPI_to_array2D":
                # TODO: 返回不一致的数据类型，让人不知所措
                data = pd.DataFrame(ret.data, columns=ret.elementNames)
            else:
                data = xr.DataArray(ret.data, dims=('lat', 'lon'),
                                    coords={'lon': np.linspace(ret.startLon, ret.endLon, ret.lonCount),
                                            'lat': np.linspace(ret.startLat, ret.endLat, ret.latCount)},
                                    name=varname)
            return data
        else:
            logger.debug(ret.request)
            raise Exception(ret.request.errorCode, ret.request.errorMessage)

    def _sel_surf(self, datasource: str, inittime: Union[str, slice, datetime] = None,
                  varname: str = None, **kwargs) -> pd.DataFrame:
        """sel surface data

        Parameters
        ----------
        datasource: str
            data source name from Daas
        inittime: str, datetime, slice
            observation datetime
        varname: str
            observation variable name, or with statistic ('SUM_', 'MAX_', 'MIN_', 'AVG_', 'COUNT_') prefix
        kwargs:
            read_from_file: read file in daas
            index_col: for statistic interface, use to group, and as the index for requested data
            lat,lon: slice of latitude and longitude
            adminCodes: region Code, 330000 is Zhejiang
            staIds: station Id, multiple Id use comma separated
            staLevels: 011,012,013 represent national, basic, ordinary
            eleValueRanges: element value range limit
            limitCnt: max return records number
            orderBy: order key
            dataProvinceId: BABJ, BEHZ ...

        Returns
        -------
        data: pd.DataFrame
            requested observation data
        """
        read_from_file = kwargs.pop('read_from_file', False)
        if read_from_file:
            url = self._sel_file(datasource, inittime)
            return url

        if datasource.startswith('SURF_CMPA'):
            return self._sel_surf_grid(datasource, inittime=inittime, varname=varname, **kwargs)

        stats_prefix = ['SUM_', 'MAX_', 'MIN_', 'AVG_', 'COUNT_']
        if any([True for p in stats_prefix if varname.startswith(p)]):
            interface = 'statSurfEle'
            para_dict = dict(elements=kwargs.get('index_col'),
                             statEles=varname)
        else:
            interface = 'getSurfEle'
            elements = varname
            if kwargs.get('index_col') is not None:
                elements = f"{varname},{kwargs.get('index_col')}"
            para_dict = dict(elements=elements)

        parameters = {
            "dataCode": self.alias.get(datasource, datasource),
            **para_dict
        }
        if kwargs.get('lat') and kwargs.get('lon'):
            parameters.update(
                {'minLat': f"{kwargs.get('lat').start}",
                 'maxLat': f"{kwargs.get('lat').stop}",
                 'minLon': f"{kwargs.get('lon').start}",
                 'maxLon': f"{kwargs.get('lon').stop}"}
            )
            interface += 'InRect'
        elif kwargs.get('adminCodes'):
            parameters.update(
                {'adminCodes': f"{kwargs.get('adminCodes')}"}
            )
            interface += 'InRegion'

        if hasattr(inittime, 'start') and hasattr(inittime, 'stop'):
            if interface.startswith('getSurf'):
                interface += 'ByTimeRange'
            parameters.update(
                {'timeRange': f"[{inittime.start:%Y%m%d%H%M%S},{inittime.stop:%Y%m%d%H%M%S}]"})
        else:
            interface += 'ByTime'
            parameters.update({'times': inittime if isinstance(inittime, str) else f"{inittime:%Y%m%d%H%M%S}"})

        if kwargs.get('staIds'):
            if kwargs.get('lat') or kwargs.get('lon'):
                raise Exception("lat/lon extent has been given.")
            if interface.startswith('getSurf'):
                interface += 'AndStaID'
            else:
                interface += 'ByStaID'
            parameters.update({'staIds': kwargs.get('staIds')})

        options = ['staLevels', 'eleValueRanges', 'limitCnt', 'orderBy', 'dataProvinceId']
        if interface.startswith('getSurf'):
            options += ['distinct', ]
        else:
            options += ['statEleValueRanges', 'hourSeparate', 'minSeparate']
        for k in options:
            if k in kwargs:
                parameters.update({k: kwargs.get(k)})

        ret = self.callAPI_to_array2D(self._user, self._password, interface, parameters, )
        if ret.request.errorCode == 0:
            data = pd.DataFrame(ret.data, columns=list(ret.elementNames))
            if kwargs.get('index_col') is not None:
                data = data.set_index(kwargs.get('index_col').split(','))
            return data
        else:
            raise Exception(ret.request.errorCode, ret.request.errorMessage)

    def _sel_upar(self, datasource: str, inittime: Union[str, slice, datetime] = None,
                  varname: str = None, **kwargs) -> pd.DataFrame:
        """sel upper data

        Parameters
        ----------
        datasource: str
            data source name from Daas
        inittime: str, datetime, slice
            observation datetime
        varname: str
            observation variable name
        kwargs:
            read_from_file: read file in daas
            index_col: for statistic interface, use to group, and as the index for requested data
            lat,lon: slice of latitude and longitude
            adminCodes: region Code, 330000 is Zhejiang
            staIds: station Id, multiple Id use comma separated
            staLevels: 011,012,013 represent national, basic, ordinary
            eleValueRanges: element value range limit
            limitCnt: max return records number
            orderBy: order key
            dataProvinceId: BABJ, BEHZ ...

        Returns
        -------
        data: pd.DataFrame
            requested observation data
        """
        read_from_file = kwargs.pop('read_from_file', False)
        if read_from_file:
            url = self._sel_file(datasource, inittime, staIds=kwargs.get('staIds', None))
            return url

        interface = 'getUparEle'
        elements = varname
        if kwargs.get('index_col') is not None:
            elements = f"{varname},{kwargs.get('index_col')}"
        para_dict = dict(elements=elements)

        parameters = {
            "dataCode": self.alias.get(datasource, datasource),
            **para_dict
        }
        if kwargs.get('lat') and kwargs.get('lon'):
            parameters.update(
                {'minLat': f"{kwargs.get('lat').start}",
                 'maxLat': f"{kwargs.get('lat').stop}",
                 'minLon': f"{kwargs.get('lon').start}",
                 'maxLon': f"{kwargs.get('lon').stop}"}
            )
            interface += 'InRect'
        elif kwargs.get('adminCodes'):
            parameters.update(
                {'adminCodes': f"{kwargs.get('adminCodes')}"}
            )
            interface += 'InRegion'

        if hasattr(inittime, 'start') and hasattr(inittime, 'stop'):
            if interface.startswith('getUpar'):
                interface += 'ByTimeRange'
            parameters.update(
                {'timeRange': f"[{inittime.start:%Y%m%d%H%M%S},{inittime.stop:%Y%m%d%H%M%S}]"})
        else:
            interface += 'ByTime'
            parameters.update({'times': inittime if isinstance(inittime, str) else f"{inittime:%Y%m%d%H%M%S}"})

        if kwargs.get('staIds'):
            if kwargs.get('lat') or kwargs.get('lon'):
                raise Exception("lat/lon extent has been given.")
            interface += 'AndStaID'
            parameters.update({'staIds': kwargs.get('staIds')})
        if kwargs.get('pLayers'):
            interface += 'AndPress'
            parameters.update({'pLayers': kwargs.get('pLayers')})
        elif kwargs.get('hLayers'):
            interface += 'AndHeight'
            parameters.update({'hLayers': kwargs.get('hLayers')})

        options = ['eleValueRanges', 'limitCnt', 'orderBy', 'dataProvinceId']
        for k in options:
            if k in kwargs:
                parameters.update({k: kwargs.get(k)})

        ret = self.callAPI_to_array2D(self._user, self._password, interface, parameters, )
        if ret.request.errorCode == 0:
            data = pd.DataFrame(ret.data, columns=list(ret.elementNames))
            if kwargs.get('index_col') is not None:
                data = data.set_index(kwargs.get('index_col').split(','))
            return data
        else:
            raise Exception(ret.request.errorCode, ret.request.errorMessage)

    def _sel_sevp(self, datasource: str, inittime: Union[str, slice, datetime] = None,
                  varname: str = None, **kwargs) -> pd.DataFrame:
        """sel surface data

        Parameters
        ----------
        datasource: str
            data source name from Daas
        inittime: str, datetime, slice
            observation datetime
        varname: str
            observation variable name, or with statistic ('SUM_', 'MAX_', 'MIN_', 'AVG_', 'COUNT_') prefix
        kwargs:
            read_from_file: read file in daas
            index_col: for statistic interface, use to group, and as the index for requested data
            lat,lon: slice of latitude and longitude
            adminCodes: region Code, 330000 is Zhejiang
            staIds: station Id, multiple Id use comma separated
            staLevels: 011,012,013 represent national, basic, ordinary
            eleValueRanges: element value range limit
            limitCnt: max return records number
            orderBy: order key
            dataProvinceId: BABJ, BEHZ ...

        Returns
        -------
        data: pd.DataFrame
            requested observation data
        """
        download = kwargs.pop('download', False)
        if download:
            url = self._sel_file(datasource, inittime, path=download)
            return url

        interface = 'getSevpEle'
        elements = varname
        if kwargs.get('index_col') is not None:
            elements = f"{varname},{kwargs.get('index_col')}"
        para_dict = dict(elements=elements)

        parameters = {
            "dataCode": self.alias.get(datasource, datasource),
            **para_dict
        }

        if hasattr(inittime, 'start') and hasattr(inittime, 'stop'):
            typh_params = {k: v for k, v in kwargs.items() if k.startswith('typh')}
            if typh_params:
                interface = 'getTyphByTimeRange'
                if kwargs.get('typhNames'):
                    interface = 'getTyphByTimeRangeAndTyphNames'
                if kwargs.get('typhCIds'):
                    interface = 'getTyphByTimeRangeAndTyphCids'
                if kwargs.get('typhNames'):
                    interface = 'getTyphByTimeRangeAndTyphGids'
                if kwargs.get('reportCenters'):
                    parameters.update({'reportCenters': kwargs.get('reportCenters')})
            else:
                interface += 'ByTimeRange'
            parameters.update(
                {'timeRange': f"[{inittime.start:%Y%m%d%H%M%S},{inittime.stop:%Y%m%d%H%M%S}]"})
        else:
            interface += 'ByTime'
            parameters.update({'times': inittime if isinstance(inittime, str) else f"{inittime:%Y%m%d%H%M%S}"})

        options = ['eleValueRanges', 'limitCnt', 'orderBy', 'dataProvinceId']
        for k in options:
            if k in kwargs:
                parameters.update({k: kwargs.get(k)})

        ret = self.callAPI_to_array2D(self._user, self._password, interface, parameters, )
        if ret.request.errorCode == 0:
            data = pd.DataFrame(ret.data, columns=list(ret.elementNames))
            if kwargs.get('index_col') is not None:
                data = data.set_index(kwargs.get('index_col').split(','))
            return data
        else:
            raise Exception(ret.request.errorCode, ret.request.errorMessage)
