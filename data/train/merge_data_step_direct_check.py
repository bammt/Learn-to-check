# -*- coding: utf-8 -*-


import json
import random
random.seed(1)
num_n2c=3700
num_c2c=300
original_file=open("gsm8k_ori_train.jsonl","r", encoding='UTF-8')
c2c_file = open("gsm8k_correct_check.txt","r", encoding='UTF-8')
n2c_file= open("gsm8k_correction.txt","r", encoding='UTF-8')
data=[]
c2c={}
n2c=[]
i=0
while  True:
    # Get next line from file
    line  =  original_file.readline()
    
    # If line is empty then end of file reached
    if  not  line :
        break
    line=json.loads(line)
   
    line['idx']=str(i)
    
    data.append(line)
    i+=1
print(len(data))
while  True:
    # Get next line from file
    line2 = c2c_file.readline()
    # If line is empty then end of file reached
    if  not  line2 :
        break
    line2=json.loads(line2)
    c2c[line2['idx']]=line2
    
while  True:
    # Get next line from file
    line  =  n2c_file.readline()
    # If line is empty then end of file reached
    if  not  line  :
        break
    line=json.loads(line)
    n2c.append(line)
    
 

sampled_data={}
temp=random.sample(n2c,num_n2c)
for element in temp:
    sampled_data[element['idx']]=element
index_list=[]
for idx in sampled_data.keys():
    index_list.append(idx)

for idx in index_list:
    if idx in c2c.keys():
        c2c.pop(idx)

temp=random.sample(list(c2c.keys()),num_c2c)
for element in temp:
    sampled_data[element]=c2c[element]
    
print(len(sampled_data))
count=0
for i in range(len(data)):
    if str(i) in sampled_data.keys():
        
        continue
    else:
        sampled_data[data[i]['idx']]=data[i]
        count+=1
        '''
        if count>=648:
            break
        '''

sys_prompt1='You are an AI assistant who can check and correct the answers very well. Based on the given text, please check if the mentioned step of the [solution] is correct.'
sys_prompt2='You are an AI assistant who can check and correct the answers very well. Please correct the [original answer] of the [Question] to get the correct answers. You should correct the error step pointed out by the [check] in the [original answer]. Please keep your reasoning process close to the [original answer] if possible.'
output_file=open("train_set.txt","w", encoding='UTF-8')
for i in range(len(data)):
    if str(i) not in sampled_data.keys():
        continue
    element=sampled_data[str(i)]
    if 'correction' in element.keys():
        
        answer_step=element['output_stp'].split('\n')
        answer_step= list(filter(None, answer_step))
        question='[Question]: '+element['question']+'\n[solution]: \n'+element['output_stp']+'\n'
        for j in range(element['wrong_step']):
            new_line={}
            new_line['system']=sys_prompt1
            #question+=answer_step[j]+'\n'
            new_line['question']=question+'Please determine if Step {} is correct.'.format(j+1)
            
            if j+1==element['wrong_step']:
                new_line['answer']='Step {} is wrong.'.format(j+1)
            else:
                new_line['answer']='Step {} is all correct.'.format(j+1)
            if i <10:
                pass
                #print(new_line['question'])
                #print(new_line['answer'])
            new_line=json.dumps(new_line,ensure_ascii=False)
            output_file.write(new_line+'\n')
        new_line2={}
        new_line2['system']=sys_prompt2
        check_str='Step {} is wrong.'.format(element['wrong_step'])
        new_line2['question']='[Question]: '+element['question']+'\n[original answer]: \n'+element['output_stp']+'\n[check]: \n'+check_str
        answer_step=element['output_stp'].split('\n')
        '''
        for j in range(element['wrong_step']-1):
            new_line2['question']+=answer_step[j]+'\n'
        '''
        correction=''
        correction_stp=list(filter(None, element['correction'].split('\n')))
        for j in range(1,len(correction_stp)-1):
            correction+=correction_stp[j]+'\n'
        correction+=correction_stp[-1]
        new_line2['answer']=correction
        if i <10:
            pass
            #print(new_line2['question'])
            #print(new_line2['answer'])
        
        new_line2=json.dumps(new_line2,ensure_ascii=False)
        output_file.write(new_line2+'\n')
    else:
        
        if 'check' in element.keys():
            answer_step=element['output_stp'].split('\n')
            answer_step= list(filter(None, answer_step))
            question='[Question]: '+element['question']+'\n[solution]: \n'+element['output_stp']+'\n'
            for j in range(len(answer_step)-1):
                new_line={}
                new_line['system']=sys_prompt1
                #question+=answer_step[j]+'\n'
                new_line['question']=question+'Please determine if Step {} is correct.'.format(j+1)
                
                new_line['answer']='Step {} is all correct.'.format(j+1)
                if i<10:
                    
                    print(new_line['question'])
                    print(new_line['answer'])
                new_line=json.dumps(new_line,ensure_ascii=False)
                output_file.write(new_line+'\n')
        else:
            new_line={}
            new_line['system']='You are an AI assistant for solving math problems that can think step by step calculate the results accurately.'
            new_line['question']=element['question']
            original_ans=element['answer'].split('\n')
            answer_str=''
            for j in range(len(original_ans)):
                if '###' not in original_ans[j]:
                    answer_str+='Step {}: '.format(j+1)+original_ans[j]+'\n'
                else:
                    answer_str+='answer:'+original_ans[j].replace('#','')
            new_line['answer']=answer_str
            if i<8:
                pass
                #print(new_line['question'])
                #print(new_line['answer'])
            new_line=json.dumps(new_line,ensure_ascii=False)
            output_file.write(new_line+'\n')

output_file.close()