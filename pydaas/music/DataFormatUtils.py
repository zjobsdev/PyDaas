#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
Modified in 2016/03/28
@author: xjunior

Modified in 2018/11/18
@author: wufeng & lr

Modified in 2023/2/6
@author: wqshen91@163.com
"""

from . import MusicDataBean


class Utils:
    """
    数据格式转换，protobuf结构和Music数据结构转换
    """

    def __init__(self):
        """
        Constructor
        """

    def convert_to_dict(self, obj):
        # 把Object对象转换成Dict对象
        dict = {}
        dict.update(obj.__dict__)
        return dict

    def convert_to_dicts(self, objs):
        # 把对象列表转换为字典列表
        obj_arr = []

        for o in objs:
            # 把Object对象转换成Dict对象
            dict = {}
            dict.update(o.__dict__)
            obj_arr.append(dict)

        return obj_arr

    def setMatrix(self, rows, cols, data):
        """
        按行列转换数据为二维数组
        """
        matrix = [[0 for col in range(cols)] for row in range(rows)]
        for i in range(rows):
            matrix[i] = data[i * cols:i * cols + cols]

        return matrix

    def setRequstInfo(self, pbRequestInfo=None):
        request = MusicDataBean.RequestInfo()
        request.errorCode = pbRequestInfo.errorCode
        request.errorMessage = pbRequestInfo.errorMessage
        request.requestElems = pbRequestInfo.requestElems
        request.requestParams = pbRequestInfo.requestParams
        request.requestTime = pbRequestInfo.requestTime
        request.responseTime = pbRequestInfo.responseTime
        request.rowCount = pbRequestInfo.rowCount
        request.takeTime = pbRequestInfo.takeTime

        return request

    def getRequestInfo(self, pbRetRequestInfo):
        """
        将protobuf类实例转换为music RequestInfo结构数据
        """
        requestInfo = MusicDataBean.RequestInfo(pbRetRequestInfo.errorCode,
                                                pbRetRequestInfo.errorMessage,
                                                pbRetRequestInfo.requestElems,
                                                pbRetRequestInfo.requestParams,
                                                pbRetRequestInfo.requestTime,
                                                pbRetRequestInfo.responseTime,
                                                pbRetRequestInfo.rowCount,
                                                pbRetRequestInfo.takeTime)

        return requestInfo

    def getArray2D(self, pbRetArray2D):
        """
        将protobuf类实例转换为music RetArray2D结构数据
        """
        retArray2D = MusicDataBean.RetArray2D(pbRetArray2D.data, pbRetArray2D.request)

        # 如果该结果数据存在，则将获取的数据，转换为二维数组格式
        if retArray2D:
            # 将获取请求信息，转换为子类对象，进行封装
            retArray2D.request = self.setRequstInfo(pbRetArray2D.request)
            retArray2D.elementNames = pbRetArray2D.elementNames
            retCode = retArray2D.request.errorCode  # 获得错误编码
            # 返回码为0，表示返回结果成功
            if retCode == 0:
                rows = retArray2D.request.rowCount  # 获得数据的行数
                retArray2D.row = rows
                cnt = len(retArray2D.data)  # 获得所有数据的个数
                # print('cnt:' + str(cnt))
                # print('row:' + str(rows))
                cols = int(cnt / rows)  # 获得数据的列数
                retArray2D.col = cols
                # print('col:' + str(cols) + '\n')
                # 将获取的数据，转换为二维数组格式
                retArray2D.data = self.setMatrix(rows, cols, retArray2D.data)

        return retArray2D

    def getDataBlock(self, pbRetDataBlock):
        """
        将protobuf类实例转换为music RetDataBlock结构数据
        """
        retDataBlock = MusicDataBean.RetDataBlock(pbRetDataBlock.dataName, pbRetDataBlock.byteArray,
                                                  pbRetDataBlock.request)
        if retDataBlock is not None:
            retDataBlock.request = self.setRequstInfo(pbRetDataBlock.request)

        return retDataBlock

    def getGridArray2D(self, pbRetGridArray2D):
        """
        将protobuf类实例转换为music RetGridArray2D结构数据
        """
        retGridArray2D = MusicDataBean.RetGridArray2D(pbRetGridArray2D.data,
                                                      pbRetGridArray2D.request)
        # 如果该结果数据存在，则将获取的数据，转换为二维数组格式
        if retGridArray2D:
            retGridArray2D.request = self.setRequstInfo(pbRetGridArray2D.request)
            retCode = retGridArray2D.request.errorCode
            if retCode == 0:
                retGridArray2D.startLat = pbRetGridArray2D.startLat
                retGridArray2D.startLon = pbRetGridArray2D.startLon
                retGridArray2D.endLat = pbRetGridArray2D.endLat
                retGridArray2D.endLon = pbRetGridArray2D.endLon
                retGridArray2D.latCount = pbRetGridArray2D.latCount
                retGridArray2D.lonCount = pbRetGridArray2D.lonCount
                retGridArray2D.lonStep = pbRetGridArray2D.lonStep
                retGridArray2D.latStep = pbRetGridArray2D.latStep
                if pbRetGridArray2D.lats is None:
                    startLat = retGridArray2D.startLat
                    latStep = retGridArray2D.latStep
                    for i in range(retGridArray2D.latCount):
                        retGridArray2D.lats.append(startLat + i * latStep)
                else:
                    retGridArray2D.lats = pbRetGridArray2D.lats
                if pbRetGridArray2D.lons is None:
                    startLon = retGridArray2D.startLon
                    lonStep = retGridArray2D.lonStep
                    for i in range(retGridArray2D.lonCount):
                        retGridArray2D.lons.append(startLon + i * lonStep)
                else:
                    retGridArray2D.lons = pbRetGridArray2D.lons
                retGridArray2D.units = pbRetGridArray2D.units
                retGridArray2D.userEleName = pbRetGridArray2D.userEleName
                rows = retGridArray2D.request.rowCount  # 获得数据的行数
                dataLen = len(retGridArray2D.data)  # 获得所有数据的个数
                cols = int(dataLen / rows)
                retGridArray2D.data = self.setMatrix(rows, cols, retGridArray2D.data)

        return retGridArray2D

    def getGridScalar2D(self, pbRetGridScalar2D):
        """
        将protobuf类实例转换为music RetGridScalar2D结构数据
        """
        retGridScalar2D = MusicDataBean.RetGridScalar2D(pbRetGridScalar2D.datas,
                                                        pbRetGridScalar2D.request)
        # 如果该结果数据存在，则将获取的数据，转换为二维数组格式
        if retGridScalar2D:
            retGridScalar2D.request = self.setRequstInfo(pbRetGridScalar2D.request)
            retCode = retGridScalar2D.request.errorCode
            if retCode == 0:
                retGridScalar2D.startLat = pbRetGridScalar2D.startLat
                retGridScalar2D.startLon = pbRetGridScalar2D.startLon
                retGridScalar2D.endLat = pbRetGridScalar2D.endLat
                retGridScalar2D.endLon = pbRetGridScalar2D.endLon
                retGridScalar2D.latCount = pbRetGridScalar2D.latCount
                retGridScalar2D.lonCount = pbRetGridScalar2D.lonCount
                retGridScalar2D.lonStep = pbRetGridScalar2D.lonStep
                retGridScalar2D.latStep = pbRetGridScalar2D.latStep
                retGridScalar2D.lats = pbRetGridScalar2D.lats
                retGridScalar2D.lons = pbRetGridScalar2D.lons
                retGridScalar2D.units = pbRetGridScalar2D.units
                retGridScalar2D.userEleName = pbRetGridScalar2D.userEleName
                #                 rows = retGridScalar2D.request.rowCount    # 获得数据的行数
                #                 dataLen = len(retGridScalar2D.data)        # 获得所有数据的个数
                #                 cols = dataLen/rows
                #                 retGridScalar2D.data = self.setMatrix(rows,cols,retGridScalar2D.data)
                retGridScalar2D.data = self.setMatrix(retGridScalar2D.latCount,
                                                      retGridScalar2D.lonCount,
                                                      retGridScalar2D.data)

        return retGridScalar2D

    def getGridVector2D(self, pbRetGridVector2D):
        """
        将protobuf类实例转换为music RetGridVector2D结构数据
        """
        retGridVector2D = MusicDataBean.RetGridVector2D(pbRetGridVector2D.u_datas,
                                                        pbRetGridVector2D.v_datas,
                                                        pbRetGridVector2D.request)
        # 如果该结果数据存在，则将获取的数据，转换为二维数组格式
        if retGridVector2D:
            retGridVector2D.request = self.setRequstInfo(pbRetGridVector2D.request)
            retCode = retGridVector2D.request.errorCode
            if retCode == 0:
                retGridVector2D.startLat = pbRetGridVector2D.startLat
                retGridVector2D.startLon = pbRetGridVector2D.startLon
                retGridVector2D.endLat = pbRetGridVector2D.endLat
                retGridVector2D.endLon = pbRetGridVector2D.endLon
                retGridVector2D.latCount = pbRetGridVector2D.latCount
                retGridVector2D.lonCount = pbRetGridVector2D.lonCount
                retGridVector2D.lonStep = pbRetGridVector2D.lonStep
                retGridVector2D.latStep = pbRetGridVector2D.latStep
                retGridVector2D.lats = pbRetGridVector2D.lats
                retGridVector2D.lons = pbRetGridVector2D.lons
                retGridVector2D.u_EleName = pbRetGridVector2D.u_EleName
                retGridVector2D.v_EleName = pbRetGridVector2D.v_EleName
                #                 rows = pbRetGridVector2D.request.rowCount    # 获得数据的行数
                #                 dataLen = len(retGridVector2D.u_datas)        # 获得所有数据的个数
                #                 cols = dataLen/rows
                rows = retGridVector2D.latCount
                cols = retGridVector2D.lonCount
                retGridVector2D.u_datas = self.setMatrix(rows, cols, retGridVector2D.u_datas)
                retGridVector2D.v_datas = self.setMatrix(rows, cols, retGridVector2D.v_datas)

        return retGridVector2D

    def getRetFilesInfo(self, pbRetFilesInfo):
        """
        将protobuf类实例转换为music RetFilesInfo结构数据
        """
        retFilesInfo = MusicDataBean.RetFilesInfo(pbRetFilesInfo.request)
        # 如果该结果数据存在，将获取请求信息，转换为子类对象，进行封装
        if retFilesInfo:
            retFilesInfo.request = self.setRequstInfo(pbRetFilesInfo.request)
            retCode = retFilesInfo.request.errorCode
            if retCode == 0:
                fileInfos = pbRetFilesInfo.fileInfos
                for i in range(len(fileInfos)):
                    retFilesInfo.fileInfos.append(self.setFileInfo(fileInfos[i]))

        return retFilesInfo

    def setFileInfo(self, pbFileInfo):
        """
        将protobuf类实例转换为music FileInfo结构数据
        """
        fileInfo = MusicDataBean.FileInfo(pbFileInfo.fileName, pbFileInfo.savePath,
                                          pbFileInfo.suffix,
                                          pbFileInfo.size, pbFileInfo.fileUrl, pbFileInfo.imgBase64,
                                          pbFileInfo.attributes)

        return fileInfo
