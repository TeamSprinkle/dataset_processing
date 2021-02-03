#!/usr/bin/env python
# coding: utf-8

# In[4]:


from soynlp.hangle import compose, decompose
import random


# # 전화 / 통화

# ① 주어 + 서술어
# 
# ② 주어 + 부사어 + 서술어
# 
# ③ 주어 + 목적어 + 서술어
# 
# ④ 주어 + 보어 + 서술어
# 
# ⑤ 주어 + 목적어 + 부사어 + 서술어

# In[16]:


# 주어
subject = ['민이', '경원', '세훈', '천우', '설아', '제니', '소담', '다솜', '가이', '규빈', '그리',           '보담', '가브리엘', '수빈', '동찬', '성현', '방지', '형근이', '이천우', '이경원', '박세훈', '김민이']

class MakeCD():
    def __init__( self, subject:list, filename:str, dataset_cnt:int = 50):
        # 조사
        self.pos = ['에게', '한테']
        # 부사
        self.Adverb = ['혹시', '빨리', '지금', '그런데', '당장', '어서']

        # 01 test1 + test2
        self.ending1 = ['주겠니', '볼까', '주자', '봐', 'ㅆ어', '줘','ㅆ다', '라', '줄 수 있어','줄 수 있느냐', '줄 수 있냐',                 '줄 수 있으십니까','주실 수 있으십니까', '주실 수 있나요', '줄래', '쥬','다오',                 '주세요', 'ㅆ냐', '달라고 했지','ㅆ니', '봐다오', 'ㅆ느냐', '볼래', 'ㅆ냐고', '주시겠습니까','ㅆ나',                'ㅆ을까', '줄래요', '주련', '줘봐', '봐줘', '주라', '봐주라', '봐봐', '보자', '봐보자', '봅시다', '보자고', '야 겠어']

        # 나중에 부탁해, 걸자 append
        # 뿌셔.....
        # 어미가 달라질 수 있는 것들 / 앞에 명사가 없으면 안되는 것들
        self.stem1 = ['해', '때려', '쳐', '뿌셔', '쌔려', '세려', '보내', '남겨', '넣어', '놓아','놔']

        # 어미가 달라질 수 있는 것들 / 앞에 명가사 없어도 되는 것들
        self.stem3 = ['걸어', '연결해', '발신해','송신해', '교신해']

        # 02 only test4 명사
        self.object_w = ['전화', '연락', '통화', '무전']

        self.list1 = []
        for i in self.stem1:
            for j in self.ending1:
                word = list(self.conjugate(i,j))
                self.list1.extend(word)

        self.list2 = []     
        for i in self.stem3:
            for j in self.ending1:
                word = list(self.conjugate(i,j))
                self.list2.extend(word)
        # for stem, eomi in testset:
        #     print('{} + {} -> {}'.format(stem, eomi, conjugate(stem, eomi)))


        # 거자 -> 걸자 
        # 거고싶어 -> 걸고싶어
        self.ending2 = ['ㄹ까','ㅂ시다', '는거 어때', '자', '고 싶어', '냐', '니', 'ㅁ']
        self.stem2 = ['보내', '하', '치', '뿌시', '쌔리', '세리', '보내', '남기', '넣으', '놓으']

        self.stem4 = ['거', '연결하', '발신하', '송신하','교신하']

        for i in self.stem2:
            for j in self.ending2:
                word2 = list(self.conjugate(i,j))
                self.list1.extend(word2)

        for i in self.stem4:
            for j in self.ending2:
                word = list(self.conjugate(i,j))
                self.list2.extend(word)
    
    
        self.Call_DS( filename, dataset_cnt)
    
    def conjugate( self, stem, ending ):

        assert ending # ending must be inserted

        l_len = len(stem)
        l_last = decompose(stem[-1])
        l_last_ = stem[-1]
        r_first = decompose(ending[0])
        r_first_ = compose(r_first[0], r_first[1], ' ') if r_first[1] != ' ' else ending[0]

        candidates = set()

        # ㄷ 불규칙 활용: 깨달 + 아 -> 깨달아
        if l_last[2] == 'ㄷ' and r_first[0] == 'ㅇ':
            l = stem[:-1] + compose(l_last[0], l_last[1], 'ㄹ')
            candidates.add(l + ending)

        # 르 불규칙 활용: 구르 + 어 -> 굴러
        if (l_last_ == '르') and (r_first_ == '아' or r_first_ == '어') and l_len >= 2:
            c0, c1, c2 = decompose(stem[-2])
            l = stem[:-2] + compose(c0, c1, 'ㄹ')
            r = compose('ㄹ', r_first[1], r_first[2]) + ending[1:]
            candidates.add(l + r)

        # ㅂ 불규칙 활용:
        # (모음조화) 더럽 + 어 -> 더러워 / 곱 + 아 -> 고와 
        # (모음조화가 깨진 경우) 아름답 + 아 -> 아름다워 / (-답, -꼽, -깝, -롭)
        if (l_last[2] == 'ㅂ') and (r_first_ == '어' or r_first_ == '아'):
            l = stem[:-1] + compose(l_last[0], l_last[1], ' ')
            if l_len >= 2 and (l_last_ == '답' or l_last_ == '곱' or l_last_ == '깝' or l_last_ == '롭'):
                c1 = 'ㅝ'
            elif r_first[1] == 'ㅗ':
                c1 = 'ㅘ'
            elif r_first[1] == 'ㅜ':
                c1 = 'ㅝ'
            elif r_first_ == '어':
                c1 = 'ㅝ'
            else: # r_first_ == '아'
                c1 = 'ㅘ'
            r = compose('ㅇ', c1, r_first[2]) + ending[1:]
            candidates.add(l + r)

        # 어미의 첫글자가 종성일 경우 (-ㄴ, -ㄹ, -ㅂ, -ㅆ)
        # 이 + ㅂ니다 -> 입니다
        if l_last[2] == ' ' and r_first[1] == ' ' and (r_first[0] == 'ㄴ' or r_first[0] == 'ㄹ' or r_first[0] == 'ㅂ' or r_first[0] == 'ㅆ'):
            l = stem[:-1] + compose(l_last[0], l_last[1], r_first[0])
            r = ending[1:]
            candidates.add(l + r)

        # ㅅ 불규칙 활용: 붓 + 어 -> 부어
        # exception : 벗 + 어 -> 벗어    
        if (l_last[2] == 'ㅅ') and (r_first[0] == 'ㅇ'):
            if stem[-1] == '벗':
                l = stem
            else:
                l = stem[:-1] + compose(l_last[0], l_last[1], ' ')
            candidates.add(l + ending)

        # 우 불규칙 활용: 푸 + 어 -> 퍼 / 주 + 어 -> 줘
        if l_last[1] == 'ㅜ' and l_last[2] == ' ' and r_first[0] == 'ㅇ' and r_first[1] == 'ㅓ':
            if l_last_ == '푸':
                l = '퍼'
            else:
                l = stem[:-1] + compose(l_last[0], 'ㅝ', r_first[2])
            r = ending[1:]
            candidates.add(l + r)

        # 오 활용: 오 + 았어 -> 왔어
        if l_last[1] == 'ㅗ' and l_last[2] == ' ' and r_first[0] == 'ㅇ' and r_first[1] == 'ㅏ':
            l = stem[:-1] + compose(l_last[0], 'ㅘ', r_first[2])
            r = ending[1:]
            candidates.add(l + r)

        # ㅡ 탈락 불규칙 활용: 끄 + 어 -> 꺼 / 트 + 었다 -> 텄다
        if (l_last_ == '끄' or l_last_ == '크' or l_last_ == '트') and (r_first[0] == 'ㅇ') and (r_first[1] == 'ㅓ'):
            l = stem[:-1] + compose(l_last[0], r_first[1], r_first[2])
            r = ending[1:]
            candidates.add(l + r)

        # 거라, 너라 불규칙 활용
        # '-거라/-너라'를 어미로 취급하면 규칙 활용
        if ending[:2] == '어라' or ending[:2] == '아라':
            if l_last[1] == 'ㅏ':            
                r = '거' + ending[1:]
            elif l_last[1] == 'ㅗ':
                r = '너' + ending[1:]
            else:
                r = ending
            candidates.add(stem + r)

        # 러 불규칙 활용: 이르 + 어 -> 이르러 / 이르 + 었다 -> 이르렀다
        if l_last_ == '르' and r_first[0] == 'ㅇ' and r_first[1] == 'ㅓ':
            r = compose('ㄹ', r_first[1], r_first[2]) + ending[1:]
            candidates.add(stem + r)

        # 여 불규칙 활용
        # 하 + 았다 -> 하였다 / 하 + 었다 -> 하였다
        if l_last_ == '하' and r_first[0] == 'ㅇ' and (r_first[1] == 'ㅏ' or r_first[1] == 'ㅓ'):
            r = compose(r_first[0], 'ㅕ', r_first[2]) + ending[1:]
            candidates.add(stem + r)

        # ㅎ (탈락) 불규칙 활용
        # 파라 + 면 -> 파랗다 / 동그랗 + ㄴ -> 동그란
        if l_last[2] == 'ㅎ' and l_last_ != '좋' and not (r_first[1] == 'ㅏ' or r_first[1] == 'ㅓ'):
            if r_first[1] == ' ':
                l = l = stem[:-1] + compose(l_last[0], l_last[1], r_first[0])
            else:
                l = stem[:-1] + compose(l_last[0], l_last[1], ' ')
            if r_first_ == '으':
                r = ending[1:]
            elif r_first[1] == ' ':            
                r = ''
            else:
                r = ending
            candidates.add(l + r)

        # ㅎ (축약) 불규칙 할용
        # 파랗 + 았다 -> 파랬다 / 시퍼렇 + 었다 -> 시퍼렜다
        if l_last[2] == 'ㅎ' and l_last_ != '좋' and (r_first[1] == 'ㅏ' or r_first[1] == 'ㅓ'):
            l = stem[:-1] + compose(l_last[0], 'ㅐ' if r_first[1] == 'ㅏ' else 'ㅔ', r_first[2])
            r = ending[1:]
            candidates.add(l + r)

        # ㅎ + 네 불규칙 활용
        # ㅎ 탈락과 ㅎ 유지 모두 맞음
        if l_last[2] == 'ㅎ' and r_first[0] == 'ㄴ' and r_first[1] != ' ':
            candidates.add(stem + ending)

        if not candidates and r_first[1] != ' ':
            candidates.add(stem + ending)

        return candidates


    def getCall( self ):
    
        '''
        데이터 생성

        subject : 사람 이름
        pos : 에게, 한테
        object_w : 전화, 연결
        stem3 : 전화해, 연결해
        Adverb : 빨리, 지금
        list1 : 쳐봐, 때려봐 // 앞에 명사가 없으면 안되는
        list2 : 걸어볼까, 연결해봐 // 앞에 명사가 없어도 되는
        '''


        result_list = list()
        ref = [1, 0]

        name = random.choice( subject )

        select = random.choice( ref )
        if select:
            select_idx = random.choice( ref )
            result_list.clear()
            result_list.append( name + self.pos[ select_idx ] )
        else:
            result_list.append( name )  

        select = random.choice( ref )
        if select:
            stem_2 = random.choice( self.Adverb )
            select_idx = random.randint( 0, len( result_list ) )
            result_list.insert( select_idx, stem_2 )

        select = random.randint( 1, 3 )
        if select == 1 :
            stem_1 = random.choice( self.object_w )
            select_idx = random.randint( 0, len( result_list ) )
            result_list.insert( select_idx, stem_1 )

            select_s = random.choice( ref )
            if select_s:
                stem_2 = random.choice( self.list1 )
                stem_2 = stem_2.split()
                for word in stem_2:
                    result_list.insert( select_idx, word )
                    select_idx += 1

        elif select == 2:
            stem_1 = random.choice( self.stem3 )
            select_idx = random.randint( 0, len( result_list ) )
            result_list.insert( select_idx, stem_1 )

        elif select == 3:
            stem_1 = random.choice( self.list2 )
            stem_1 = stem_1.split()
            select_idx = random.randint( 0, len( result_list ) )
            for word in stem_1:
                result_list.insert( select_idx, word )
                select_idx += 1

            select_s = random.choice( ref )
            if select_s:
                stem_1 = random.choice( self.object_w )
                select_idx = random.randint( 0, len( result_list ) )
                result_list.insert( select_idx, stem_1 )

        return result_list

    # 라벨 생성
    def getLabel( self, Sentence ):
        label = list()

        for word in Sentence:
            if word.endswith( self.pos[0]) or word.endswith(self.pos[1] ):
                word = word[:-2]

            if word in subject:
                label.append( 'S-Target' )
            else:
                label.append( 'O' )

        return label
    
    def Call_DS( self, file_name:str, linecnt:int ):
        with open(filename, 'w') as f:
            f.write('question,label\n')

        SENTDIC = dict()
        while len( SENTDIC ) != linecnt:
            count = ( linecnt ) - len( SENTDIC )

            for cnt in range( count ):
                result = self.getCall()
                SENTDIC[' '.join(result)] = ' '.join(self.getLabel(result))

        for key, value in SENTDIC.items():
            with open(file_name, 'a') as f:
                f.write(f'{key},{value}\n')


# In[18]:


makecalldate = MakeCD( subject, 'test.csv', 100 )


# In[ ]:




