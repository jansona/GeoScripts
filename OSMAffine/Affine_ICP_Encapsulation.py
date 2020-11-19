# File      :Affine_ICP_Encapsulation.py
# Author    :WJ
# Fuction   :
# Time      :2020/11/10
# Version   :
# Amend     :


def Affine_ICP(osm, map, OSM, MaxDistance=50, MaxIteration=200):
    osm=osm
    map=map

    class ICP:
        import numpy as np
        map = np.array(0) # 模型集
        osm = np.array(0)  # 初始数据集
        Y = []  # 最近点集
        X = []
        AF01 = [[1, 0],
                [0, 1]]
        AF02 = [[0],
                [0]]
        J = 0
        def __init__(self,osm,map):
            ICP.osm=osm
            ICP.map=map
            print('开始仿射ICP匹配')
            print('----------------------------------')
        def __del__(self):
            print('----------------------------------')
            print('仿射ICP匹配完成\n')


        def ca_Y(self,MaxDistance=20):  # 求最近点集Y MaxDistanc为搜索最邻近点时的范围
            import numpy as np
            from scipy.spatial import KDTree
            y = []
            D = []
            R = []
            P = ICP.map
            X = ICP.osm

            Tree = KDTree(P, 2)  # 建立KDTree
            for i in range(X.shape[0]):
                idx1 = Tree.query(X[i, :], k=1, distance_upper_bound=MaxDistance)
                # 返回一个数组，第一位为最近距离，第二位为最近点索引
                if idx1[1] == P.shape[0]:  # 若在给定范围内无最近点，则第二位返回建立KDTree的数组长度
                    R.append(i)
                else:
                    y.append(P[idx1[1]])
                    D.append(idx1[0])
            R.sort(reverse=True)  # 反向排序，根据索引删除不符合要求的数据
            X = list(X)
            for i in range(len(R)):
                del X[R[i]]
            ICP.X = np.array(X)
            y = np.array(y)
            ICP.Y = y
        # 仿射变换方法------------------------------------------------------
        def affine_fit(self):
            import numpy as np
            q = ICP.X

            p = ICP.Y


            if len(q) != len(p) or len(q) < 1:
                print("原始点和目标点的个数必须相同.")
                return False

            dim = len(q[0])  # 维度
            if len(q) < dim:
                print("点数小于维度.")
                return False

                # 新建一个空的 维度 x (维度+1) 矩阵 并填满
            c = [[0.0 for a in range(dim)] for i in range(dim + 1)]
            for j in range(dim):
                for k in range(dim + 1):
                    for i in range(len(q)):
                        qt = list(q[i]) + [1]
                        c[k][j] += qt[k] * p[i][j]

                        # 新建一个空的 (维度+1) x (维度+1) 矩阵 并填满
            Q = [[0.0 for a in range(dim)] + [0] for i in range(dim + 1)]
            for qi in q:
                qt = list(qi) + [1]
                for i in range(dim + 1):
                    for j in range(dim + 1):
                        Q[i][j] += qt[i] * qt[j]

                        # 判断原始点和目标点是否共线，共线则无解. 耗时计算，如果追求效率可以不用。

            # 其实就是解n个三元一次方程组
            def gauss_jordan(m, eps=1.0 / (10 ** 10)):
                (h, w) = (len(m), len(m[0]))
                for y in range(0, h):
                    maxrow = y
                    for y2 in range(y + 1, h):
                        if abs(m[y2][y]) > abs(m[maxrow][y]):
                            maxrow = y2
                    (m[y], m[maxrow]) = (m[maxrow], m[y])
                    if abs(m[y][y]) <= eps:
                        return False
                    for y2 in range(y + 1, h):
                        c = m[y2][y] / m[y][y]
                        for x in range(y, w):
                            m[y2][x] -= m[y][x] * c
                for y in range(h - 1, 0 - 1, -1):
                    c = m[y][y]
                    for y2 in range(0, y):
                        for x in range(w - 1, y - 1, -1):
                            m[y2][x] -= m[y][x] * m[y2][y] / c
                    m[y][y] /= c
                    for x in range(h, w):
                        m[y][x] /= c
                return True

            M = [Q[i] + c[i] for i in range(dim + 1)]
            if not gauss_jordan(M):
                print("错误，原始点和目标点也许是共线的.")
                return False
            AF01 = []
            AF02 = []
            for j in range(dim):
                for i in range(dim):
                    AF01.append(M[i][j + dim + 1])
                AF02.append(M[dim][j + dim + 1])
            AF01 = np.array(AF01).reshape(2, 2)
            AF02 = np.array(AF02).reshape(2, 1)
            AF01 = np.around(AF01,10)
            AF02 = np.around(AF02,10)


            if (AF01 == ICP.AF01).all():
                if (AF02 == ICP.AF02).all():
                    ICP.J = -1
                    print('迭代收敛！')
            else:
                temp = np.matrix(np.dot(ICP.AF01, ICP.X.transpose()) + ICP.AF02)
                temp = temp.transpose()
                err = []
                for i in range(len(temp)):
                    err.append(((temp[i, 0] - ICP.Y[i, 0]) ** 2 + (temp[i, 1] - ICP.Y[i, 1]) ** 2) ** 0.5)
                error = np.mean(err)
                print('err:', error)
                ICP.AF01 = AF01
                ICP.AF02 = AF02
                tem = np.array(np.dot(ICP.AF01, ICP.osm.transpose()) + ICP.AF02).transpose()
                if (ICP.osm == tem).all():
                    ICP.J=-1
                    print('迭代收敛！')
                else:
                    ICP.osm = tem


    import time
    import numpy as np
    start = time.clock()
    A = ICP(osm,map)
    A.ca_Y(MaxDistance)
    A.affine_fit()

    TEM = np.matrix(np.dot(A.AF01, OSM.transpose()) + A.AF02)
    OSM_af = TEM.transpose()

    # 迭代
    i = 1
    while (MaxIteration - i > 0):
        i+=1
        print("正在进行第 %d 次匹配。"%i)
        A.ca_Y(MaxDistance)
        A.affine_fit()
        if A.J == 0:

            TEM = np.matrix(np.dot(A.AF01, OSM_af.transpose()) + A.AF02)
            OSM_af = TEM.transpose()
        else:
            break

    if A.J == 0:
        print('迭代未收敛。')
        print('\n总匹配次数为%d次。' % i)
    else:
        print('\n总匹配次数为%d次。' % (i - 1))
    end = time.clock()
    print('Running time: %s Seconds\t' % (end - start))
    return OSM_af


# if __name__ == '__main__':
#     # 测试-----------------------------------------------------------------------------------------------------------
#     import numpy as np
#     data1 = np.loadtxt('D:\\STUDY\\Python\\DATA\\intersectpoints\\pointcloud1\\roadpoint_map.txt', delimiter=',')
#     map_p = np.array(data1[:, 0:2])
#     data2 = np.loadtxt('D:\\STUDY\\Python\\DATA\\intersectpoints\\pointcloud1\\roadpoint_osm.txt', delimiter=',')
#     osm_p = np.array(data2[:, 0:2])
#     data3 = np.loadtxt('D:\\STUDY\\Python\\DATA\\intersectpoints\\pointcloud1\\Source-z90y180.txt', delimiter=',')
#     OSM = np.array(data3[:, 0:2])
#     OSM_AF = Affine_ICP(osm_p,map_p,OSM,20,100)
#     np.savetxt("输出.txt",OSM_AF,delimiter=',')
#     # 测试-----------------------------------------------------------------------------------------------------------
