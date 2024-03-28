# -*- coding: utf-8 -*-
# @Author: wqshen
# @Email: wqshen91@gmail.com
# @Date: 2023/6/14 17:42
# @Last Modified by: wqshen

import os
import sys
import argparse
import logzero
import pandas as pd
import xarray as xr
from typing import Union
from logzero import logger
from datetime import datetime
from pydaas import DaasClient


def typecast(string: str) -> Union[int, float, str]:
    """cast string into int/float/str in sequence"""
    try:
        return int(string)
    except ValueError:
        try:
            return float(string)
        except Exception:
            return string


def args_parser(s: str) -> Union[slice, list, int, float, str]:
    """standardization of special char usage in args

    Parameters
    ----------
    s: str
        argument string, special chars and its meaning as following,
        - , represents slice from it's left to right, step can also be place the last
        , , represents list from split by ,

    Returns
    -------
    Union[slice, list, int, float, str]
    """
    if '-' in s:
        s_ = [typecast(item) for item in s.split('-')]
        if len(s_) == 2:
            return slice(*s_)
        elif len(s_) == 3:
            return list(range(*s_))
        else:
            raise Exception("s can only be split to 2 or 3")
    elif ',' in s:
        return [typecast(item) for item in s.split(',')]
    else:
        return typecast(s)


def time_parser(s: str) -> Union[slice, list]:
    """parser time string

    Parameters
    ----------
    s: str
        - , represents date range from it's left to right, time freq can also be place the last
        , , represents list from split by ,

    Returns
    -------
    Union[pd.DatetimeIndex, list]
    """
    parse_t = lambda t: datetime.strptime(t, '%Y%m%d%H')

    if '-' in s:
        s_ = s.split('-')
        if len(s_) == 2:
            return slice(*map(parse_t, s_))
        elif len(s_) == 3:
            return pd.date_range(*map(parse_t, s_[:2]), freq=s_[-1]).to_list()
        else:
            raise Exception("s can only be split to 2 or 3")
    else:
        return list(map(parse_t, s.split(',')))


def _main():
    example_text = """Example:
     # 读取欧洲中心细网格2023021912起报的预报时效为24小时的500hPa相对湿度，并保存为ECMWF.2023021912.024.RHU.500.nc文件
     daas_dump ECMWF_P 2023021912 -f 24 --level 500 -v RHU --outfile ./ECMWF.2023021912.024.RHU.500.nc
     
     # 限定纬度为20-40N，经度为110-130E，预报时效为12和24读取
     daas_dump ECMWF_P 2023021912 -f 12,24 --level 500 --lat 20-40 --lon 110-130 -v RHU -o 10
     
     # 限定为单点 (30N,120E) 12-24小时500hPa相对湿度时序
     daas_dump ECMWF_P 2023021912 -f 12-24 --level 500 --lat 30 --lon 120 -v RHU -o 10
     
     # 限定为 (30N,120E)、(40N,130E) 两个点的24小时预报
     daas_dump ECMWF_P 2023021912 -f 24 --level 500 --lat 30,40 --lon 120,130 -v RHU -o 10
     
     # 读取欧洲中心集合预报的地面温度场
     daas_dump ECMWF_C3E 2023021912 -f 24 --lat 20-40 --lon 110-130 -v TEM -o 10
     
     # 读取中国气象局全球模式的地面温度场
     daas_dump CMA_GFS 2023021912 -f 24 --lat 20-40 --lon 110-130 -v TEM -o 10
     
     daas_dump CMA_SH3 2023021912 --download ./ -o 10

     # 读取杭州站2023021912到2023022012的逐小时降水观测，设置输出表的索引列为Station_Name
     daas_dump SURFACE 2023021912-2023022012 -v Station_Name,Lon,Lat,Alti,Datetime,PRE_1H --staIds 58457 --index_col Station_Name

     # 读取浙江省2023021912到2023022012的逐小时降水观测，设置输出表的索引列为Station_Name
     daas_dump SURFACE 2023021912-2023022012 -v Station_Name,Lon,Lat,Alti,Datetime,PRE_1H --adminCodes 330000 --index_col Station_Name
     
     # 读取2023072612-2023072912的杜苏芮台风（DOKSURI）路径预报
     daas_dump SEVP_ZJ_WEFC_TYP_WT 2023072612-2023072912 -v Datetime,TYPH_Name,V_CHN_NAME,Num_Nati,Bul_Center,Lat,Lon,PRS,Validtime --reportCenters BABJ --typhNames DOKSURI 
     """

    parser = argparse.ArgumentParser(description='Daas Data Dumper', epilog=example_text,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('datasource', help='data source name')
    parser.add_argument('inittime', help='model initial time or observation time', type=time_parser)
    parser.add_argument('-f', '--fh', help='model forecast hour', type=args_parser)
    parser.add_argument('--leadtime', help='model leadtime', type=time_parser)
    parser.add_argument('-e', '--outfile', type=str, help='output netcdf file name')
    parser.add_argument('-c', '--complevel', type=int, help='output netcdf4 compress level',
                        default=5, choices=range(10))
    parser.add_argument('-v', '--varname', help='model variable names', type=args_parser)
    parser.add_argument('-x', '--lon', help='longitude point or range', type=args_parser)
    parser.add_argument('-y', '--lat', help='latitude point or range', type=args_parser)
    parser.add_argument('-p', '--level', help='pressure level point or range', type=int)
    parser.add_argument('-d', '--download', help='path to download raw file', type=str)
    parser.add_argument('-l', '--staIds', help='Station Ids', type=str)
    parser.add_argument('-t', '--offset-inittime', help='offset inittime (hours) to variable',
                        type=str)
    parser.add_argument('--name_map', help='map variable name to new', type=args_parser)
    parser.add_argument('-u', '--user', type=str, help='User name')
    parser.add_argument('-s', '--password', type=str, help='password')
    parser.add_argument('-n', '--njobs', type=int, help='parallel thread numbers', default=1,
                        choices=range(4))
    parser.add_argument('-o', '--loglevel', type=int, help='logger level', default=20,
                        choices=range(10, 51, 10))

    extra_args = ['index_col', 'staLevels', 'eleValueRanges', 'limitCnt', 'orderBy', 'dataProvinceId',
                  'statEleValueRanges', 'hourSeparate', 'minSeparate', 'distinct', 'adminCodes',
                  'reportCenters', 'typhNames', 'typhCIds', 'typhGIds']
    for a in extra_args:
        parser.add_argument(f"--{a}", help=f'extra kwargs {a}', type=str)

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    logzero.loglevel(args.loglevel)
    logger.debug(args)

    extra_kwargs = dict()
    if args.lon is not None:
        extra_kwargs['lon'] = args.lon
    if args.lat is not None:
        extra_kwargs['lat'] = args.lat
    if args.level is not None:
        extra_kwargs['level'] = args.level
    if args.staIds is not None:
        extra_kwargs['staIds'] = args.staIds
    if args.download is not None:
        extra_kwargs['download'] = args.download
    for a in extra_args:
        if getattr(args, a) is not None:
            extra_kwargs[a] = getattr(args, a)

    with DaasClient(args.user, args.password) as mc:
        mc.njobs = args.njobs
        logger.debug(f"{args.datasource}, {args.inittime}, {args.fh}, {args.varname}, {extra_kwargs}")
        dataset = mc.sel(args.datasource, args.inittime, args.fh, args.varname, args.leadtime,
                         merge=True, **extra_kwargs)
        logger.debug(dataset)

        if args.offset_inittime is not None:
            dataset['time'] = pd.to_datetime(dataset.time.values) + pd.to_timedelta(
                args.offset_inittime)

        if args.name_map is not None:
            dataset = dataset.rename({args.name_map[0]: args.name_map[1]})

    logger.info(f"-------------\n{dataset}")
    if args.outfile is not None:
        _, file_extension = os.path.splitext(args.outfile)
        if file_extension in ('.nc', '.nc4') and isinstance(dataset, xr.Dataset):
            comp = dict(zlib=True, complevel=args.complevel, dtype='f4')
            encoding = {var: comp for var in [*dataset.data_vars, 'lon', 'lat']}
            dataset.to_netcdf(args.outfile, encoding=encoding)
        elif file_extension in ('.txt', '.csv'):
            if isinstance(dataset, xr.DataArray):
                dataset.to_dataframe().to_csv(args.outfile)
            else:
                dataset.to_csv(args.outfile)
        else:
            raise NotImplementedError("Only support nc, nc4, txt, csv extentsion.")


if __name__ == '__main__':
    _main()
