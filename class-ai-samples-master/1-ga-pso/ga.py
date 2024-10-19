#-*- encoding:utf-8 -*-
'''
@File    :   ga.py,
@Time    :   Tue Dec 15 10:45:42 CST 2020
@Version :   1.0,
@Contact :   https://blog.csdn.net/cyril_ki/article/details/108589078
@License :   GPL
@Desc    :   遗传算法的应用示例

Modified by: HAO Jiasheng, for the teaching @ UESTC

'''

import numpy as np
import matplotlib.pyplot as plt
import random
from pylab import mpl

class Population:
    # 种群的设计
    def __init__(self, size, chrom_size, cp=0.8, mp=0.1, gen_max=200):
        # 种群信息合
        self.individuals = []          # 个体集合
        self.fitness = []              # 个体适应度集
        self.selector_probability = [] # 个体选择概率集合
        self.new_individuals = []      # 新一代个体集合

        self.elitist = {'chromosome':[0, 0], 'fitness':0, 'age':0} # 最佳个体的信息

        self.size = size # 种群所包含的个体数
        self.chromosome_size = chrom_size # 个体的染色体长度
        self.crossover_probability = cp   # 个体之间的交叉概率
        self.mutation_probability = mp    # 个体之间的变异概率
         
        self.generation_max = gen_max # 种群进化的最大世代数
        self.age = 0                  # 种群当前所处世代

        self.interval = []
        self.fitness_func = None
          
        # 随机产生初始个体集，并将新一代个体、适应度、选择概率等集合以 0 值进行初始化
        v = 2 ** self.chromosome_size - 1
        for i in range(self.size):
            self.individuals.append([random.randint(0, v), random.randint(0, v)])
            self.new_individuals.append([0, 0])
            self.fitness.append(0)
            self.selector_probability.append(0)

    # 基于轮盘赌博机的选择
    def decode(self, chromosome):
        interval = self.interval
        '''将一个染色体 chromosome 映射为区间 interval 之内的数值'''
        d = interval[1] - interval[0]
        n = float (2 ** self.chromosome_size -1)
        return (interval[0] + chromosome * d / n)
              
    def evaluate(self):
        '''用于评估种群中的个体集合 self.individuals 中各个个体的适应度'''
        sp = self.selector_probability
        for i in range (self.size):
            
            (x, y) = (self.decode(self.individuals[i][0]), 
                      self.decode(self.individuals[i][1]))
            
            self.fitness[i] = self.fitness_func (x, y)
                                                
        ft_sum = sum (self.fitness)
        for i in range (self.size):
            sp[i] = self.fitness[i] / float (ft_sum)   # 得到各个个体的生存概率
        for i in range (1, self.size):
            sp[i] = sp[i] + sp[i-1]   # 需要将个体的生存概率进行叠加，从而计算出各个个体的选择概率

    # 轮盘赌博机（选择）
    def select(self):
        (t, i) = (random.random(), 0)
        for p in self.selector_probability:
            if p > t:
                break
            i = i + 1
        return i

    # 交叉
    def cross(self, chrom1, chrom2):
        p = random.random()    # 随机概率
        n = 2 ** self.chromosome_size -1
        if chrom1 != chrom2 and p < self.crossover_probability:
            t = random.randint(1, self.chromosome_size - 1)   # 随机选择一点（单点交叉）
            mask = n << t    # << 左移运算符
            # & 按位与运算符：参与运算的两个值,如果两个相应位都为1,则该位的结果为1,否则为0
            (r1, r2) = (chrom1 & mask, chrom2 & mask)   
            mask = n >> (self.chromosome_size - t)
            (l1, l2) = (chrom1 & mask, chrom2 & mask)
            (chrom1, chrom2) = (r1 + l2, r2 + l1)
        return (chrom1, chrom2)

    # 变异
    def mutate(self, chrom):
        p = random.random ()
        if p < self.mutation_probability:
            t = random.randint (1, self.chromosome_size)
            mask1 = 1 << (t - 1)
            mask2 = chrom & mask1
            if mask2 > 0:
                chrom = chrom & (~mask2)  # ~ 按位取反运算符：对数据的每个二进制位取反,即把1变为0,把0变为1 
            else:
                chrom = chrom ^ mask1   # ^ 按位异或运算符：当两对应的二进位相异时，结果为1 
        return chrom

    # 保留最佳个体
    def reproduct_elitist (self):
        # 与当前种群进行适应度比较，更新最佳个体
        j = -1
        for i in range (self.size):
            if self.elitist['fitness'] < self.fitness[i]:
                j = i
                self.elitist['fitness'] = self.fitness[i]
        if (j >= 0):
            self.elitist['chromosome'][0] = self.individuals[j][0]
            self.elitist['chromosome'][1] = self.individuals[j][1]
            self.elitist['age'] = self.age

    # 进化过程
    def evolve(self):
        indvs = self.individuals
        new_indvs = self.new_individuals
        # 计算适应度及选择概率
        self.evaluate()
        # 进化操作
        i = 0
        while True:
            # 选择两个个体，进行交叉与变异，产生新的种群
            idv1 = self.select()
            idv2 = self.select()
            # 交叉
            (idv1_x, idv1_y) = (indvs[idv1][0], indvs[idv1][1])
            (idv2_x, idv2_y) = (indvs[idv2][0], indvs[idv2][1])
            (idv1_x, idv2_x) = self.cross(idv1_x, idv2_x)
            (idv1_y, idv2_y) = self.cross(idv1_y, idv2_y)
            # 变异
            (idv1_x, idv1_y) = (self.mutate(idv1_x), self.mutate(idv1_y))
            (idv2_x, idv2_y) = (self.mutate(idv2_x), self.mutate(idv2_y))
            (new_indvs[i][0], new_indvs[i][1]) = (idv1_x, idv1_y)  # 将计算结果保存于新的个体集合self.new_individuals中
            (new_indvs[i+1][0], new_indvs[i+1][1]) = (idv2_x, idv2_y)
            # 判断进化过程是否结束
            i = i + 2         # 循环self.size/2次，每次从self.individuals 中选出2个
            if i >= self.size:
                break
        
        # 最佳个体保留
        # 如果在选择之前保留当前最佳个体，最终能收敛到全局最优解。
        self.reproduct_elitist()

        # 更新换代：用种群进化生成的新个体集合 self.new_individuals 替换当前个体集合
        for i in range (self.size):
            self.individuals[i][0] = self.new_individuals[i][0]
            self.individuals[i][1] = self.new_individuals[i][1]
        self.age += 1

    def run(self, interval, fitness_func, plotfunc):
        self.interval = interval
        self.fitness_func = fitness_func
        '''根据种群最大进化世代数设定了一个循环。
        在循环过程中，调用 evolve 函数进行种群进化计算，并输出种群的每一代的个体适应度最大值、平均值和最小值。'''
        maxf = []
        for i in range (self.generation_max):
            self.evolve ()
            print(i, max (self.fitness), sum (self.fitness)/self.size, min (self.fitness))
            maxf.append(max(self.fitness))

        # 输出最优解
        (x, y) = (self.decode(self.elitist['chromosome'][0]),
                  self.decode(self.elitist['chromosome'][1]))
        result = (u'【结果】当前最优值: {:.4f}, 位置: ({:.4f}, {:.4f}), 代数: {}'\
                  .format(self.elitist['fitness'], x, y, self.elitist['age']))

        t = [i for i in range(self.generation_max)]
        plotfunc(t, maxf)

        return result


def fitness_func(x, y):
    '''适应度函数，可以根据个体的两个染色体计算出该个体的适应度'''
    
    fitness = x * np.sin(4 * np.pi * x) - y * np.sin(4 * np.pi * y + np.pi) + 1
    return fitness

def plot_func(t, maxf):
    mpl.rcParams['font.sans-serif'] = ['SimHei']
    plt.figure()
    plt.plot(t, maxf, color='red', marker='.', ms=15)
    plt.rcParams['axes.unicode_minus'] = False
    plt.margins(0)
    plt.xlabel(u"迭代次数")  # X轴标签
    plt.ylabel(u"最优值")  # Y轴标签
    plt.title(u"迭代过程")  # 标题
    plt.show()

	
if __name__ == '__main__':

    group_size   = 150   # 种群的个体数量
    chrom_length = 15   # 染色体长度
    cross_p      = 0.8  # 交叉概率
    mut_p        = 0.1  # 变异概率
    gen_max      = 150  # 进化最大世代数
    
    ga = Population (group_size, chrom_length, cross_p, mut_p, gen_max)
    interval = [-1.0, 2.0]
    result = ga.run(interval, fitness_func, plot_func)

    print(result)


