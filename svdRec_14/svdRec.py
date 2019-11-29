'''14_1 相似度计算
2019_11_29
'''

import numpy as np

def ecludSim(inA, inB):
    '''
    Function Description:
        欧式距离
    Parameters:
        inA, inB:输入向量
    Returns:
        相似度
    Time:
        2019_11_29
    '''      
    return 1.0 / (1.0 + np.la.norm(inA - inB))

def pearsSim(inA, inB):
    '''
    Function Description:
        皮尔逊相关系数
    Parameters:
        inA, inB:输入向量
    Returns:
        相似度
    Time:
        2019_11_29
    '''      
    #此时两个向量完全相关
    if len(inA) < 3:
        return 1.0
    return 0.5 + 0.5 * np.corrcoef(inA, inB, rowvar=0)[0][1]

def cosSim(inA, inB):
    '''
    Function Description:
        余弦相似度
    Parameters:
        inA, inB:输入向量
    Returns:
        相似度
    Time:
        2019_11_29
    '''      
    num = float(inA.T * inB)
    denom = np.la.norm(inA) * np.la.norm(inB)
    return 0.5 + 0.5 * (num / denom)

'''14_2 基于物品相似度的推荐引擎
2019_11_29
'''    

def loadExData():
    '''
    Function Description:
        加载数据，菜肴矩阵
        行:代表人
        列:代表菜肴名词
        值:代表人对菜肴的评分，0代表未评分
    Parameters:
        None
    Returns:
        菜肴矩阵
    Time:
        2019_11_29
    '''      
    return[[0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 5],
           [0, 0, 0, 3, 0, 4, 0, 0, 0, 0, 3],
           [0, 0, 0, 0, 4, 0, 0, 1, 0, 4, 0],
           [3, 3, 4, 0, 0, 0, 0, 2, 2, 0, 0],
           [5, 4, 5, 0, 0, 0, 0, 5, 5, 0, 0],
           [0, 0, 0, 0, 5, 0, 1, 0, 0, 5, 0],
           [4, 3, 4, 0, 0, 0, 0, 5, 5, 0, 1],
           [0, 0, 0, 4, 0, 4, 0, 0, 0, 0, 4],
           [0, 0, 0, 2, 0, 2, 5, 0, 0, 1, 2],
           [0, 0, 0, 0, 5, 0, 0, 0, 0, 4, 0],
           [1, 0, 0, 0, 0, 0, 0, 1, 2, 0, 0]]


def standEst(dataMat, user, simMeas, item):
    '''
    Function Description:
        基于物品相似度的推荐引擎
        计算某用户未评分物品，以对该物品和其他物品的用户的物品相似度，然后进行综合评分
    Parameters:
        dataMat:训练数据集
        user:用户编号
        simMeas:相似度计算方法
        item:未评分的物品编号
    Returns:
        评分(0~5之间的值)
    Time:
        2019_11_29
    '''      
    #得到数据集中的物品数目
    n = np.shape(dataMat)[1]
    #初始化两个评分值
    simTotal = 0.0
    ratSimTotal = 0.0
    #遍历行中的每个物品(对用户评过分的物品进行遍历，并将它与其他物品进行比较)
    for j in range(n):
        userRating = dataMat[user, j]
        #如果某个物品的评分值为0，则跳过这个物品
        if userRating == 0:
            continue
        #寻找两个用户都评级的物品
        #变量overLap给出的是两个物品当中已经被评分的那个元素的索引ID
        #logical_and计算x1和x2元素的逻辑与
        overLap = np.nonzero(np.logical_and(dataMat[:, item].A > 0, dataMat[:, j].A > 0))[0]
        #如果相似度为0，则两者没有任何重合元素，终止本次循环
        if len(overLap) == 0:
            similarity = 0
        #如果存在重合的物品，则基于重合物重新计算相似度
        else:
            similarity = simMeas(dataMat[overLap, item], dataMat[overLap, j])
        print('the %d and %d simlarity is: %f' % (item, j, similarity))
        #相似度会不断增加，每次计算时还考虑相似度和当前用户评分的乘积
        #similarity 用户相似度   userRating 用户评分
        simTotal += similarity
        ratSimTotal += similarity * userRating
    if simTotal == 0:
        return 0
    #通过除以所有的评分和，对上述相似度评分的乘积进行归一化，使得最后评分在0~5之间，这些评分用来对预测值进行排序
    else:
        return ratSimTotal / simTotal

def recommend(datamat, user, N=3, simMeas=conSim, estMethod=standEst):
    '''
    Function Description:
        推荐引擎
    Parameters:
        dataMat:训练数据集
        user:用户编号
        N:产生的N个推荐结果
        simMeas:相似度计算方法
        estMethod:推荐引擎方法
    Returns:
        评分(0~5之间的值)
    Time:
        2019_11_29
    '''          
    #寻找未评级的物品
    #对给定的用户建立一个未评分的物品列表
    unratedItems = np.nonzero(datamat[user, :].A == 0)[1]
    #如果不存在未评分物品，那么就退出函数
    if len(unratedItems) == 0:
        return ('you rated everything')
    #物品的编号和评分值
    itemScores = []
    #在未评分的物品上进行循环
    for item in unratedItems:
        estimatedScore = estMethod(datamat, user, simMeas, item)
        #寻找前N个未评级的物品，调用standEst()来产生该物品的预测得分，该物品的编号和估计值会放在一个元素列表itemScores中
        itemScores.append((item, estimatedScore))
    #返回元素列表，第一个就是最大值
    return sorted(itemScores, key=lambda jj: jj[1], reverse=True)[:N]








