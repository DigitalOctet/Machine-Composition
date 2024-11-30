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
coeff_melody = 1 #旋律组合奖励系数
de_major_notes = [0, 2, 4, 5, 7, 9, 11]  #大调
de_xmajor_notes = [1, 3, -1, 6, 8 ,10]
major_notes = [8, 10, 12, 13, 15, 17, 19, 20]  #选择调式，此处以C大调为例
jump_weights = {
    1: 0.7,    #符合自然流动（1度跳跃）
    2: 1.0,    
    3: 0.9,    #最流畅的二三度跳跃
    4: 0.4,
    5: 0.3,    #较为突兀
    6: 0.1,
}
JUMP_SCORE = 100 #总分100

def fitness(Individual):
    pts = 0
    pitch = Individual.pitches[::]
    self_check(pitch)   #自检
    pts += rhythm(pitch)  #节奏型得分
    pts += various_average(pitch)  #均值方差得分
    pts += pitch_jump(pitch)   #音符跨度得分
    pts += pitch_variety(pitch) #音符种类数得分
    pts += scale_in_major_notes(pitch)  #检查音符是否在特定调式中
    pts += calculate_melodic_reasonableness(pitch) #按小节评估音乐片段的音阶合理性
    pts += melody(pitch) #旋律合理得分
    return pts

#自检
def self_check(pitch):
    assert len(pitch) == 32, 'len pitch must be 32'

    strong = []
    midstrong = []
    for i in range(0,32,8):
        strong.append(pitch[i])
    for i in range(4,32,8):
        midstrong.append(pitch[i])
    assert not (0 in strong), 'strong beat cant be 0'
    assert not (0 in midstrong), 'midstrong beat cant be 0'

#节奏型加分
def rhythm(pitch):
    pts = 0
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
    print('Rhythm scores:', pts)
    return pts
    
#方差均值得分
def various_average(pitch):
    pts = 0
    pitch_fmt = pitch[::]
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
    print('Mean, Variance score:', pts)
    return pts


#音高间隔加分、罚分
def pitch_jump(pitch):
    pts = 0
    pitch_simpl = [x for x in pitch if x != 0]
    de_list = []
    for i in range(len(pitch_simpl)-1):
        de = abs(pitch_simpl[i+1] - pitch_simpl[i])
        de_list.append(de)
        if de > 6:      #跳音惩罚
            pts += -int(de**1.5)
    if de_list.count(1) > 3:      #半音惩罚
            pts += -40

    de = max(pitch_simpl) - min(pitch_simpl)
    if de > 18:
        pts -=de*5
        
    print('Pitch interval score:', pts)
    return pts


#音符种类多样型加分
def pitch_variety(pitch):
    pts = 0
    pitch_set = set(pitch)
    pitch_kinds = len(pitch_set)
    if pitch_kinds in (6,7,8,9,10,11,12):
        pts += 100
    elif pitch_kinds <=3:
        pts += -200
    elif pitch_kinds >16:
        pts += -pitch_kinds*5
    print('Pitch variety score:', pts)
    return pts


#检查音符是否在调式中
def scale_in_major_notes(pitch):
    pts = 0
    pitch_simple = [x for x in pitch if x != 0]
    de_simple = []
    for pit in pitch_simple:
        de = (pit - main_pitch) % 12
        de_simple.append(de)
        if de == 0: 
            pts += 30 #主音
        if de == 2: 
            pts += 15 #上主音
        if de == 4:
            pts += 20  #中音
        if de == 5:
            pts += 12  #下属音
        if de == 7:
            pts += 25 #属音
        if de == 9:
            pts += 20 #下中音
        if de == 11:
            pts += 6 #导音

    #出现频率过高惩罚
    maxfreq = len(pitch_simple)//3
    
    for i in (0,2,4,5,7,9,11):
        p_cnt = de_simple.count(i)
        if p_cnt > maxfreq:
            pts += -20*(p_cnt-maxfreq)**2   

    if pitch[-1] == main_pitch:  #最后一个音为主音C4加100分
        pts += 40
    if pitch[-1] == main_pitch + 12: #最后一个音为主音C5加80分
        pts += 40
    print('Pitch harmony score:', pts*coeff_mode)
    return pts*coeff_mode

#按小节评估音乐片段的音阶进行合理性, 使得能有更多和弦出现
def calculate_melodic_reasonableness(pitch):
    if len(pitch) != 32:
        raise ValueError("必须是32位!")
    #将音乐划分为四小节
    bars = [ [x for x in pitch[i : i+8] if x !=0 ] for i in range(0, 32, 8)]
    #对每小节进行评分
    def evaluate_bar(bar) :
        valid_jumps = 0   #合理跳跃数
        total_jumps = 0   #总跳跃数
        direction_changes = 0  #方向变化总数
        prev_note = bar[0]
        prev_direction = None
        for i in range(1, len(bar)):
            curr_note = bar[i]
            #跳跃幅度检查
            if curr_note in major_notes and prev_note in major_notes:
                jump = abs(major_notes.index(curr_note) - major_notes.index(prev_note))
                weight = jump_weights.get(jump, 0)
                valid_jumps += weight
            total_jumps += 1  #总跳跃数
            # 检查方向变化
            if curr_note != prev_note:
                curr_direction = 1 if curr_note > prev_note else -1
                if prev_direction is not None and curr_direction != prev_direction:
                    direction_changes += 1
                prev_direction = curr_direction
            prev_note = curr_note
        
        #评分计算
        jump_score = valid_jumps/ total_jumps * JUMP_SCORE      #跳跃平滑性得分
        direction_score = max(0, 100 - direction_changes * 10)  #方向平滑性得分
        return jump_score, direction_score
    bar_scores = []
    for bar in bars:
        jump_score, direction_score = evaluate_bar(bar)
        bar_scores.append({
            "jump_score" : jump_score,
            "direction_score" : direction_score,
            "bar_total_score" : 0.7 * jump_score + 0.3 * direction_score
        })
    
    #整体评分
    overall_jump_score = sum(bar["jump_score"] for bar in bar_scores) / len(bar_scores)
    overall_direction_score = sum(bar["direction_score"] for bar in bar_scores) / len(bar_scores)
    overall_score = int(overall_jump_score + overall_direction_score)
    print(f"Melodic score : {overall_score : .2f}")
    return overall_score
          
def melody(pitch):  
    pts = 0
    pitch_rgl = []
    for i in pitch:
        if i == 0:
            continue
        if (i-main_pitch)%12 in de_major_notes: #调式音
            pitch_rgl.append(de_major_notes.index((i-main_pitch)%12)+1)
        else:
            pitch_rgl.append(de_xmajor_notes.index((i-main_pitch)%12)+1.5)
    if [1,2,3] in pitch_rgl:
        pts += 10
    if [1,3,5] in pitch_rgl:
        pts += 12
    if [3,4,5] in pitch_rgl:
        pts += 12
    if [2,3,1] in pitch_rgl:
        pts += 12
    if [3,2,1] in pitch_rgl:
        pts += 10
    if [5,3,1] in pitch_rgl:
        pts += 8
    if [1,7,6] in pitch_rgl:
        pts += 5
    if [1,3,1] in pitch_rgl:
        pts += 8
    if [3,3,5] in pitch_rgl:
        pts += 8
    if [2,1,6] in pitch_rgl:
        pts += 8
    if [5,6,5] in pitch_rgl:
        pts += 5
    if [6,5,3] in pitch_rgl:
        pts += 7
    if [3,6,5] in pitch_rgl:
        pts += 9
    if [6,1,2] in pitch_rgl:
        pts += 4
    return pts*coeff_melody
          


if __name__ == "__main__": 
    from random import randint
    class Indivdual():
            def __init__(self,li):
                self.pitches = li

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
    #久石让-"菊次郎的夏天"前奏
    li4 = [17,24,29,24,13,20,25,20,
           15,22,27,22,20,27,32,27,
           17,24,29,24,13,20,25,20,
           15,22,27,22,20,27,32,27]
    #F-777-"Triple fuse"移调
    li5 = [10,22,10,20,6,20,6,17,
           13,17,13,20,8,15,8,17,
           10,22,10,20,6,20,6,27,
           25,17,13,20,8,15,8,17]
    #F-777-"One Last Hope"主旋律
    li6 = [18,0,0,0,18,25,0,17,
           0,18,0,0,0,18,20,0,
           18,17,18,0,0,0,18,25,
           0,17,0,18,0,0,0,30]
    #Yiruma-"River Flows In You"主旋律移调
    li7 = [13,15,13,12,13,0,8,0,
          13,15,13,12,13,0,0,0,
          13,15,13,12,13,15,17,18,
          20,17,15,13,12,0,8,0]
    #Kr1z-"A Hero's Life"主旋律微调
    li8 = [10,10,13,10,10,13,0,12,
          6,6,12,6,8,8,13,8,
          10,10,13,10,10,13,0,12,
          6,6,13,15,12,8,12,12]
    #Iming-"Glacial Maze"第一段移调
    li9 = [15,0,0,15,0,15,18,20,
          10,0,0,10,0,10,13,0,
          15,0,0,15,0,15,18,0,
          22,0,0,20,0,13,18,17]
    #Iming-"Glacial Maze"主旋律二段移调
    li10 = [3,15,13,15,10,8,6,8,
          3,15,13,15,8,0,6,0,
          3,15,13,15,10,8,6,5,
          6,13,8,13,6,0,5,0]
    #罗大佑-"童年"节选
    li11 = [17,17,0,17,17,15,15,0,
          13,13,0,13,15,13,10,8,
          8,8,0,8,10,8,15,17,
          13,0,0,0,0,0,0,0]
    #Waterflame-"ThunderZone v2"节选
    li12 = [15,13,15,0,15,0,15,17,
          18,0,17,0,17,0,17,18,
          20,0,15,0,15,0,22,18,
          17,0,18,17,13,15,17,18]
    #Plun-"Orca"节选移调
    li13 = [22,24,25,20,0,8,13,17,
          15,13,12,13,0,20,15,13,
          8,13,12,13,0,15,17,20,
          18,17,13,15,0,17,15,13]
    #F-777 "Dance Of The Violin"主旋律微调
    li14 = [17,10,17,13,18,22,20,18,
          20,17,13,12,0,8,12,13,
          17,10,17,13,18,22,20,18,
          20,17,13,15,0,25,0,24]
    #Quree-"One Forgotten Night"主旋律
    li15 = [10,17,22,25,0,0,24,0,
          0,20,0,0,17,0,15,17,
          20,0,0,22,0,0,15,0,
          0,20,0,0,17,0,15,17]
    li16 = [10,17,22,25,0,0,24,0,
          0,25,0,0,24,0,25,27,
          29,0,0,22,0,0,17,0,
          27,0,0,25,0,24,0,0]
    #帕赫贝尔-"D大调卡农" 节选移调
    li17 = [20,0,17,18,20,0,17,18,
          20,8,10,12,13,15,17,18,
          17,0,13,15,17,0,5,6,
          8,10,8,6,8,13,12,13]
    li18 = [10,0,13,12,10,0,8,6,
          8,6,5,6,8,10,12,13,
          10,0,13,12,13,0,12,13,
          12,10,12,13,15,17,18,20]
    #Plum-"Terrasphere" 移调
    li19 = [20,0,0,13,13,15,17,18,
          20,0,25,0,24,0,20,0,
          13,0,0,8,8,13,15,17,
          18,17,15,13,17,0,15,0]
    li20 = [20,0,25,0,25,24,22,20,
          20,0,15,18,17,18,17,15,
          13,0,8,20,15,17,15,13,
          13,0,0,0,0,0,0,0]
    #Катюша（喀秋莎）微调移调
    li21 = [10,0,0,12,13,0,0,10,
          13,13,12,10,12,0,5,0,
          12,0,0,13,15,0,0,12,
          15,15,13,12,10,0,0,0]
    li22 = [17,0,22,0,20,0,22,20,
          18,18,17,15,17,0,10,0,
          0,18,0,15,17,0,0,13,
          15,15,13,12,10,0,0,0]
    #suno ai做的钢琴曲
    li23 = [3,0,10,8,0,13,0,15,
          0,10,18,17,0,13,10,6,
          3,0,10,8,0,15,0,13,
          0,8,15,13,0,8,6,1]
    t = 0
    times = 0
    while t<500 and times < 70:
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
        times += 1

    print(t)
    print(li)
    print('--------ref----------')
    test1 = Indivdual(li1)
    print(fitness(test1))

