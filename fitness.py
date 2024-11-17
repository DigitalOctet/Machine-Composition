# 1 = F3, 8 = C4, 20 = C5, 27 = G5
# 0 不能出现在强拍和中强拍


'''rhythm的编码如下
rhythm = {[1,0,0,0]:0,
          [1,1,0,0]:4,
          [1,0,1,0]:2,
          [1,0,0,1]:1,
          [1,1,1,0]:6,
          [1,1,0,1]:5,
          [1,0,1,1]:3,
          [1,1,1,1]:7}
'''
import numpy as np

main_pitch = 8  #规定主音或调式
idl_mean = 12   #理想均值
idl_variance = 10     #理想方差
coeff_mean = 0.2    #均值偏离惩罚系数
coeff_variance = 0.3  #方差偏离惩罚系数
coeff_mode = 1   #调式符合奖励系数

def fitness(Individual):

    pts = 0
    #自检
    pitch = Individual.pitch[::]
    assert len(pitch) == 32, 'len pitch must be 32'

    strong = []
    midstrong = []
    for i in range(0,32,8):
        strong.append(pitch[i])
    for i in range(4,32,8):
        midstrong.append(pitch[i])
    assert not (0 in strong), 'strong beat cant be 0'
    assert not (0 in midstrong), 'midstrong beat cant be 0'

    #节奏形
    pitch_div = [pitch[i:i+4] for i in range(0, 32, 4)]
    rhythm = []
    for bar in pitch_div:
        vp = 0 
        for i in range(1,4):
            if bar[i] > 0:
                vp += 2**(i-1)
        rhythm.append(vp)

    if rhythm[-1] == 5:
        pts += -100   #切分音结尾惩罚

    for i in range(4):  #节奏重复奖励      
        if rhythm[i] == rhythm[i+4]:
            pts += 20
    for i in range(0,8,2):
        if rhythm[i] == rhythm[i+1]:
            pts += 5
    for i in range(0,8,4):     
        if rhythm[i] == rhythm[i+2]:
            pts += 10

    

    rhythm_set = set(rhythm)
    rhythm_kinds = len(rhythm_set)

    if rhythm_kinds == 1:   #节奏种类数惩奖
        pts += -200
    elif rhythm_kinds == 2:
        pts += -100
    elif rhythm_kinds == 3:
        pts += 0
    elif rhythm_kinds in (4,5,6):
        pts += 100
    elif rhythm_kinds > 6:
        pts += -rhythm_kinds*10

    print(rhythm)
    print('pts after rhythm:', pts)
    
    
    ####
    pitch_fmt = Individual.pitch[::]
    for i in range(31):
        if pitch_fmt[i+1] == 0:
            pitch_fmt[i+1] = pitch_fmt[i]

    pitch_fmt_array = np.array(pitch_fmt)

    mean = np.mean(pitch_fmt_array)
    de_mean = abs(mean-idl_mean)
    pts -= int(coeff_mean*de_mean**2)

    variance = np.var(pitch_fmt_array)
    de_variance = abs(variance-idl_variance)
    pts -= int(coeff_variance*de_variance**2)

    print(mean, variance)
    print('pts after mean, variance:', pts)

    ####
    pitch_simpl = [x for x in Individual.pitch if x != 0]
    for i in range(len(pitch_simpl)-1):
        de = abs(pitch_simpl[i+1] - pitch_simpl[i])
        if de > 6:      #跳音惩罚
            pts += -de**2
        if de == 1:      #半音惩罚
            pts += -40


    de = max(pitch_simpl) - min(pitch_simpl)
    if de > 18:
        pts -=de*5

    print('pts after interval:', pts)

    pitch_set = set(Individual.pitch)
    pitch_kinds = len(pitch_set)
    if pitch_kinds in (6,7,8,9,10,11,12):
        pts += 100
    elif pitch_kinds <=3:
        pts += -200
    elif pitch_kinds >16:
        pts += -pitch_kinds*5
    print('pts after pitch vary:', pts)

    for pit in pitch_fmt:
        de = (pit - main_pitch) % 12
        if de == 0 : 
            pts += 30*coeff_mode #主音
        if de == 2: 
            pts += 15*coeff_mode  #上主音
        if de == 4:
            pts += 20*coeff_mode  #中音
        if de == 5:
            pts += 12*coeff_mode  #下属音
        if de == 7:
            pts += 25*coeff_mode #属音
        if de == 9:
            pts += 20*coeff_mode #下中音
        if de == 11:
            pts += 6*coeff_mode #导音

    if pitch_fmt[-1] == main_pitch:  #最后一个音为主音C4加100分
        pts += 100*coeff_mode
    if pitch_fmt[-1] == main_pitch + 12: #最后一个音为主音C5加80分
        pts += 80*coeff_mode
    print('pts after pitch harmony:', pts)


    return pts

if __name__ == "__main__": 
    from random import randint
    class Indivdual():
            def __init__(self,li):
                self.pitch = li

    #小红帽前两节
    li1 = [8,10,12,13,15,0,12,8,
            20,0,17,13,15,15,12,0,
            8,10,12,13,15,12,10,8,
            10,0,12,0,10,0,15,0]
    #啥也不是
    li2 = [2,3,1,12,3,0,2,18,
            20,10,27,13,25,25,12,0,
            18,20,22,23,25,12,20,8,
            20,10,22,10,20,0,15,20]
    li3 = [22,23,21,22,23,20,22,18,
            20,10,27,13,25,25,12,0,
            18,20,22,23,25,22,20,8,
            20,10,22,10,20,0,15,20]
    t = 0
    while t<500:
        li=[]
        for i in range(32):
            if i%4 != 0 and randint(0,2) == 0:
                li.append(0)
            else:
                li.append(randint(8,20))
        
        '''
                C4 : 8
                D4 : 10
                E4 : 12
                F4 : 13
                G4 : 15
                A4 : 17
                B4 : 19
                C5 : 20
        '''  
        

        test = Indivdual(li)
        #test2 = Indivdual(li2)
        #test3 = Indivdual(li3)
        #print(fitness(test1))
        t = fitness(test)

    print(t)
    print(li)
    print('--------ref----------')
    test1 = Indivdual(li1)
    print(fitness(test1))

