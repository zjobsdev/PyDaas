PyDaas
======

**高级的、易用的 气象大数据云平台 在线数据读取包**

> 大数据云平台常包含有各类常规和非常规观测资料、数值模式资料、服务产品等,
  数据格式多种多样，平台针对各类数据有不同的接口支持，使用时需要根据数据代码和该数据可用接口来获取数据，
  这要求我们在使用时打开网页平台进行一系列操作才能获取数据，在一定程度上增加了获取数据的复杂度。

PyDaas库通过对大数据云平台的Python SDK进行进一步封装来简化接口的调用和数据的获取，其设计理念和使用逻辑与
`PyMDFS <https://github.com/zjobsdev/PyMDFS>`_ 库保持一致，

1. 高度简化用户调用接口
2. 使用主流的pandas和xarray数据结构

安装方法
^^^^^^^^^^^^^^

.. code:: shell

    pip install pydaas


简单上手
^^^^^^^^^^^^^^^

`pydaas <https://github.com/zjobsdev/pydaas>`_ 中最常用的类为 **DaasClient** ，
它承担了从大数据云平台中读取和转换数据格式的重要功能。

**DaasClient 介绍**

- 初次使用，请配置库路径下 config/client.config 文件中的 `music_server` 和 `music_port`
- 用户名和密码可以指定在库路径下的 client.config 文件中的 `music_user` 和 `music_password`
- 用户名和密码也可以在实例化 **DaasClient** 类时使用 `user` and `password` 参数指定
- 使用 **DaasClient** 类读取数据时，主要通过调用其 `sel` 方法来实现，该方法包含以下常用参数

  - `datasource`, 大数据云平台中的数据名称代码，也可以在库路径下config/alias.yaml 配置常用数据别名，简化复杂度
  - `inittime`, 数值模式的起报时间或观测数据的观测时间
  - `fh`, 模式预报时效（仅针对模式数据）
  - `varname`, 变量名, 对应于子类数据路径后移植到最后的数据目录路径，以 */* 连接
  - `level`, 模式垂直层（仅针对模式数据）
  - `lat`, 维度切片
  - `lon`, 经度切片

通过下面十个例子来了解 PyDaas的用法


Ex 1 从大数据平台中读取CMA-GFS数值模式0-24h总降水量数据，读取范围为20-40N,110-130E
----------------------------------------------------------------------------------------------------

.. note:: 通过指定 `lat` 、 `lon` 为slice对象来设定读取的数据经纬度范围

.. code-block:: python

    from datetime import datetime, timedelta
    from pydaas import DaasClient

    dc = DaasClient()
    inittime = datetime.utcnow().replace(minute=0, second=0, microsecond=0, hour=12) - timedelta(days=2)
    dar = dc.sel('CMA_GFS', inittime, fh=24, varname='TPE', lat=slice(20, 40), lon=slice(110, 130))
    print(dar)

Ex 2 从大数据平台中读取ECMWF数值模式预报(30N,120E) 0-72h逐3小时850hPa温度时间序列
----------------------------------------------------------------------------------------------------

.. note:: 通过指定 `fh` 为 slice 对象来设定读取的预报时效范围

.. code-block:: python

    from datetime import datetime, timedelta
    from pydaas import DaasClient

    dc = DaasClient()
    inittime = datetime.utcnow().replace(minute=0, second=0, microsecond=0, hour=12) - timedelta(days=2)
    dar = dc.sel('ECMWF_P', inittime, fh=slice(0, 72), varname='RHU', level=850, lat=30, lon=120)
    print(dar)

Ex 3 从大数据平台中读取ECMWF数值模式预报(30N,120E)、(25N,119E)两个点的0-72小时逐3小时850hPa相对湿度
----------------------------------------------------------------------------------------------------

.. note::  通过指定 `lat` 、 `lon` 列表来制定要读取的数据经纬度点

.. code-block:: python

    from datetime import datetime, timedelta
    from pydaas import DaasClient

    dc = DaasClient()
    inittime = datetime.utcnow().replace(minute=0, second=0, microsecond=0, hour=12) - timedelta(days=2)
    dar = dc.sel('ECMWF_P', inittime, fh=slice(0, 72), varname='RHU', level=850, lat=[30,35], lon=[120,122])
    print(dar)

Ex 4 从大数据平台中读取ECMWF-EPS集合预报24小时时效2米气温数据，读取范围为20-40N,110-130E
----------------------------------------------------------------------------------------------------

.. note:: 大数据云平台没有提供集合预报数据所有成员的一次性读取接口，因此程序内部采取迭代的方式读取各成员的数据再进行拼接，需要保证调用次数不超过分钟调用次数上限

.. code-block:: python

    from datetime import datetime, timedelta
    from pydaas import DaasClient

    dc = DaasClient()
    inittime = datetime.utcnow().replace(minute=0, second=0, microsecond=0, hour=12) - timedelta(days=2)
    dar = dc.sel('ECMWF_C3E', inittime, fh=24, varname='TEM', lat=slice(20, 40), lon=slice(110, 130))
    print(dar)

Ex 5 从大数据平台中下载华东区域快速更新同化模式的某一起报时次数据
----------------------------------------------------------------------------------------------------

.. note:: 通过 `download` 参数指定下载路径，路径量较大时，请耐心等待下载完毕

.. code-block:: python

    from datetime import datetime, timedelta
    from pydaas import DaasClient

    dc = DaasClient()
    inittime = datetime.utcnow().replace(minute=0, second=0, microsecond=0, hour=12) - timedelta(days=2)
    dar = dc.sel('CMA_SH3', datetime(2023, 6, 5, 0), download='/data')
    print(dar)

Ex 6 从大数据平台中读取地面逐小时观测杭州站（58457）10天的逐小时降水，附加站点信息
----------------------------------------------------------------------------------------------------

.. note::

    1. 站点数据读取返回一个DataFrame对象
    2. 通过参数 `index_col` 设定观测时间 (Datetime) 为表格的索引列
    3. 通过参数 `staIds` 指定读取的区站号为杭州 (58457)
    4. 通过参数 `orderBy` 指定结果按照观测时间降序排列



.. code-block:: python

    from datetime import datetime, timedelta
    from pydaas import DaasClient

    dc = DaasClient()
    nowtime = datetime.utcnow().replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)
    times = slice(nowtime - timedelta(days=10), nowtime)

    variable = 'Station_Id_C,Station_Name,Lon,Lat,Alti,Datetime,PRE_1H'
    dar = dc.sel('SURFACE', times, varname=variable, index_col='Datetime', staIds='58457', orderBy='Datetime:desc')
    print(dar)


Ex 7 从大数据平台中读取110-130E,20-40N范围内过去24小时累计降水
----------------------------------------------------------------------------------------------------

.. note::

    1. 使用统计接口计算累计量时，变量名只能为单个变量
    2. 通过参数 `index_col` 指定索引列为 'Station_Id_C,Station_Name,Lon,Lat,Alti'
    3. 通过设定参数 `lon` 、 `lat` 为 slice 对象指定读取的观测数据经纬度范围
    4. 通过参数 `orderBy` 指定结果按照观测时间降序排列

.. code-block:: python

    from datetime import datetime, timedelta
    from pydaas import DaasClient

    dc = DaasClient()
    nowtime = datetime.utcnow().replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)
    times = slice(nowtime - timedelta(days=1), nowtime)

    variable = 'SUM_PRE_1H'
    dar = dc.sel('SURFACE', times, varname=variable,
                  index_col='Station_Id_C,Station_Name,Lon,Lat,Alti',
                  lon=slice(110, 130), lat=slice(20, 40),
                  orderBy='Station_Id_C:asc')
    print(dar)


Ex 8 从大数据平台中读杜苏芮台风信息
----------------------------------------------------------------------------------------------------

.. note::

    1. 通过参数 `reportCenters` 指定报告中心，如 BABJ 为国家局
    2. 通过设定参数 `typhNames` 为 DOKSURI 指定 杜苏芮 台风
    3. 通过参数 `orderBy` 指定结果按照设定的变量升/降序排列

.. code-block:: python

    from datetime import datetime, timedelta
    from pydaas import DaasClient

    dc = DaasClient()
    variable = 'Datetime,TYPH_Name,V_CHN_NAME,Num_Nati,Bul_Center,Lat,Lon,PRS,Validtime'
    inittime = datetime(2023, 7, 29, 12)
    dar = dc.sel('SEVP_ZJ_WEFC_TYP_WT', slice(inittime - timedelta(days=1), inittime),
                 varname=variable, reportCenters='BABJ', typhNames='DOKSURI',
                 orderBy='Num_Nati:asc,Bul_Center:asc,Validtime:asc,Datetime:asc')
    print(dar)

Ex 9 从大数据平台中读取CMAPS 5km多元融合逐小时降水数据集
----------------------------------------------------------------------------------------------------

.. code-block:: python

    from datetime import datetime
    from pydaas import DaasClient

    dc = DaasClient()
    dar = dc.sel('CMPA_HOR', datetime(2023, 6, 5, 0), varname='PRE',  lat=slice(20, 40), lon=slice(110, 130))
    print(dar)

Ex 10 从大数据平台中读取CLDAS 5km日最低气温数据
----------------------------------------------------------------------------------------------------

.. code-block:: python

    from datetime import datetime
    from pydaas import DaasClient
    dc = DaasClient()
    dar = dc.sel('CLDAS_D', datetime(2023, 6, 14, 8), varname='MNT', level=None,)
    print(dar)


**daas_dump** 命令行工具
^^^^^^^^^^^^^^^^^^^^^^^^^^^

用法:
    daas_dump.py [-h] [-f FH] [-e OUTFILE] [-c COMPLEVEL] [-v VARNAME] [-x LON] [-y LAT] [-p LEVEL] [-d DOWNLOAD] [-l STAIDS] [-t OFFSET_INITTIME] [--name_map NAME_MAP] [-u USER]
                 [-s PASSWORD] [-o LOGLEVEL] [--index_col INDEX_COL] [--staLevels STALEVELS] [--eleValueRanges ELEVALUERANGES] [--limitCnt LIMITCNT] [--orderBy ORDERBY]
                 [--dataProvinceId DATAPROVINCEID] [--statEleValueRanges STATELEVALUERANGES] [--hourSeparate HOURSEPARATE] [--minSeparate MINSEPARATE] [--distinct DISTINCT]
                 [--adminCodes ADMINCODES] [--reportCenters REPORTCENTERS] [--typhNames TYPHNAMES] [--typhCIds TYPHCIDS] [--typhGIds TYPHGIDS]
                 datasource inittime

位置参数:
    +------------+------------------------+
    | 选项       | 说明                   |
    +------------+------------------------+
    | datasource | 数据名称               |
    +------------+------------------------+
    | inittime   | 模式起报时间或观测时间 |
    +------------+------------------------+
可选参数:

    +-------------------------------------------------------+---------------------------------------------------------------------------------+
    | 选项                                                  | 说明                                                                            |
    +-------------------------------------------------------+---------------------------------------------------------------------------------+
    | -h, --help                                            | 显示帮助信息并退出                                                              |
    +-------------------------------------------------------+---------------------------------------------------------------------------------+
    | -f FH, --fh FH                                        | 数值模式预报时效                                                                |
    +-------------------------------------------------------+---------------------------------------------------------------------------------+
    | -e OUTFILE, --outfile OUTFILE                         | 输出的文件位置，支持 nc 、 diamond4、 txt 、csv                                 |
    +-------------------------------------------------------+---------------------------------------------------------------------------------+
    | -c COMPLEVEL, --complevel COMPLEVEL                   | netcdf4格式压缩级别                                                             |
    +-------------------------------------------------------+---------------------------------------------------------------------------------+
    | -v VARNAME, --varname VARNAME                         | 模式变量名或观测变量名                                                          |
    +-------------------------------------------------------+---------------------------------------------------------------------------------+
    | -x LON, --lon LON                                     | 经度范围或点， 110-130 表示从110到130E， 110/130 表示单独是经度点，需配合纬度点 |
    +-------------------------------------------------------+---------------------------------------------------------------------------------+
    | -y LAT, --lat LAT                                     | 纬度范围或点， 用法同上                                                         |
    +-------------------------------------------------------+---------------------------------------------------------------------------------+
    | -p LEVEL, --level LEVEL                               | 气压层                                                                          |
    +-------------------------------------------------------+---------------------------------------------------------------------------------+
    | -d DOWNLOAD, --download DOWNLOAD                      | 下载模式数据的存放地址                                                          |
    +-------------------------------------------------------+---------------------------------------------------------------------------------+
    | -l STAIDS, --staIds STAIDS                            | 区站号                                                                          |
    +-------------------------------------------------------+---------------------------------------------------------------------------------+
    | -t OFFSET_INITTIME, --offset-inittime OFFSET_INITTIME | 对输出变量偏移小时数                                                            |
    +-------------------------------------------------------+---------------------------------------------------------------------------------+
    | --name_map NAME_MAP                                   | 对输出变量做变量名映射                                                          |
    +-------------------------------------------------------+---------------------------------------------------------------------------------+
    | -u USER, --user USER                                  | 用户名                                                                          |
    +-------------------------------------------------------+---------------------------------------------------------------------------------+
    | -s PASSWORD, --password PASSWORD                      | 密码                                                                            |
    +-------------------------------------------------------+---------------------------------------------------------------------------------+
    | -o LOGLEVEL, --loglevel LOGLEVEL                      | 日志级别                                                                        |
    +-------------------------------------------------------+---------------------------------------------------------------------------------+
    | --index_col INDEX_COL                                 | 观测数据表的索引列                                                              |
    +-------------------------------------------------------+---------------------------------------------------------------------------------+
    | --staLevels STALEVELS                                 | 观测站点级别                                                                    |
    +-------------------------------------------------------+---------------------------------------------------------------------------------+
    | --eleValueRanges ELEVALUERANGES                       | 要素值域区间                                                                    |
    +-------------------------------------------------------+---------------------------------------------------------------------------------+
    | --limitCnt LIMITCNT                                   | 输出的要素记录个数                                                              |
    +-------------------------------------------------------+---------------------------------------------------------------------------------+
    | --orderBy ORDERBY                                     | 表的排序方式                                                                    |
    +-------------------------------------------------------+---------------------------------------------------------------------------------+
    | --dataProvinceId DATAPROVINCEID                       | 观测数据所属省份编号，330000 为浙江                                             |
    +-------------------------------------------------------+---------------------------------------------------------------------------------+
    | --statEleValueRanges STATELEVALUERANGES               | 统计要素值域区间                                                                |
    +-------------------------------------------------------+---------------------------------------------------------------------------------+
    | --hourSeparate HOURSEPARATE                           | extra kwargs hourSeparate                                                       |
    +-------------------------------------------------------+---------------------------------------------------------------------------------+
    | --minSeparate MINSEPARATE                             | extra kwargs minSeparate                                                        |
    +-------------------------------------------------------+---------------------------------------------------------------------------------+
    | --distinct DISTINCT                                   | extra kwargs distinct                                                           |
    +-------------------------------------------------------+---------------------------------------------------------------------------------+
    | --adminCodes ADMINCODES                               | 行政区代码， 330000 为浙江                                                      |
    +-------------------------------------------------------+---------------------------------------------------------------------------------+
    | --reportCenters REPORTCENTERS                         | 台风发报中心，BABJ 为国家局                                                     |
    +-------------------------------------------------------+---------------------------------------------------------------------------------+
    | --typhNames TYPHNAMES                                 | 台风名称                                                                        |
    +-------------------------------------------------------+---------------------------------------------------------------------------------+
    | --typhCIds TYPHCIDS                                   | 台风国内编号                                                                    |
    +-------------------------------------------------------+---------------------------------------------------------------------------------+
    | --typhGIds TYPHGIDS                                   | 台风国际编号                                                                    |
    +-------------------------------------------------------+---------------------------------------------------------------------------------+

示例:
     1. 读取欧洲中心细网格2023021912起报的预报时效为24小时的500hPa相对湿度，并保存为ECMWF.2023021912.024.RHU.500.nc文件
     daas_dump ECMWF_P 2023021912 -f 24 --level 500 -v RHU --outfile ./ECMWF.2023021912.024.RHU.500.nc

     2. 限定纬度为20-40N，经度为110-130E，预报时效为12和24读取
     daas_dump ECMWF_P 2023021912 -f 12/24 --level 500 --lat 20-40 --lon 110-130 -v RHU -o 10

     3. 限定为单点 (30N,120E) 12-24小时500hPa相对湿度时序
     daas_dump ECMWF_P 2023021912 -f 12-24 --level 500 --lat 30 --lon 120 -v RHU -o 10

     4. 限定为 (30N,120E)、(40N,130E) 两个点的24小时预报
     daas_dump ECMWF_P 2023021912 -f 24 --level 500 --lat 30/40 --lon 120/130 -v RHU -o 10

     5. 读取欧洲中心集合预报的地面温度场
     daas_dump ECMWF_C3E 2023021912 -f 24 --lat 20-40 --lon 110-130 -v TEM -o 10

     6. 读取中国气象局全球模式的地面温度场
     daas_dump CMA_GFS 2023021912 -f 24 --lat 20-40 --lon 110-130 -v TEM -o 10

     7. 下载华东区域快速更新同化模式2023021912起报的所有文件
     daas_dump CMA_SH3 2023021912 --download ./ -o 10

     8. 读取杭州站2023021912到2023022012的逐小时降水观测，设置输出表的索引列为Station_Name
     daas_dump SURFACE 2023021912-2023022012 -v Station_Name,Lon,Lat,Alti,Datetime,PRE_1H --staIds 58457 --index_col Station_Name

     9. 读取浙江省2023021912到2023022012的逐小时降水观测，设置输出表的索引列为Station_Name
     daas_dump SURFACE 2023021912-2023022012 -v Station_Name,Lon,Lat,Alti,Datetime,PRE_1H --adminCodes 330000 --index_col Station_Name

     10. 读取2023072612-2023072912的杜苏芮台风（DOKSURI）路径预报
     daas_dump SEVP_ZJ_WEFC_TYP_WT 2023072612-2023072912 -v Datetime,TYPH_Name,V_CHN_NAME,Num_Nati,Bul_Center,Lat,Lon,PRS,Validtime --reportCenters BABJ --typhNames DOKSURI
