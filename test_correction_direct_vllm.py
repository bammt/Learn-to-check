import os
os.environ["CUDA_VISIBLE_DEVICES"]="0"

import torch
import json
from transformers import LlamaForCausalLM, LlamaTokenizer, AutoTokenizer, AutoModelForCausalLM, AutoConfig
from vllm import SamplingParams, LLM
import argparse
from tqdm import tqdm
import json
model_path='llama2-13b' #the path of original llama2-13B
check_path='llama2-13b' #replace the path with your fine-tuned ckpt
max_new_tokens = 1024
orignal_file  =  open("test.jsonl","r", encoding='UTF-8')
output_file  =  open("correction_direct.txt","w", encoding='UTF-8')
data=[]

while  True:
    # Get next line from file
    line  =  orignal_file.readline()
    # If line is empty then end of file reached
    if  not  line  :
        break
    line=json.loads(line)
    data.append(line)
orignal_file.close()
i=0


prompt = []
while i<len(data):
    question=data[i]['question']
    #
    instruction='System: \nYou are an AI assistant for solving math problems that can think step by step calculate the results accurately.\n\n'+'Human: \n'+question+'\n\nAssistant: \n'          
    prompt.append(instruction)
    i += 1
sampling_params_1 = SamplingParams(
    temperature=0,
    top_k=-1,
    top_p=1,
    use_beam_search=False,
    repetition_penalty=1.2,
    max_tokens=max_new_tokens
)
sampling_params_2 = SamplingParams(
    temperature=0.5,
    top_k=30,
    top_p=0.85,
    use_beam_search=False,
    repetition_penalty=1.2,
    max_tokens=max_new_tokens
)
sampling_params_3 = SamplingParams(
    temperature=0.5,
    top_k=30,
    top_p=0.85,
    use_beam_search=False,
    repetition_penalty=1.2,
    max_tokens=max_new_tokens
)
llm = LLM(model=check_path, tokenizer=model_path)

outputs = llm.generate(prompt, sampling_params_1)

i = 0
step_check_prompt = []
while i<len(data):
    question=data[i]['question']
    generated_output = outputs[i].outputs[0].text.replace('</s>','').replace('<unk>','')        
    print(generated_outputs)

    data[i]['output1']=generated_output
    
    original_output=data[i]['output1'].strip().split('\n')
    step_num=len(original_output)-1
    data[i]['cnt_step']=step_num
   
    
    
    prompt='System: \nYou are an AI assistant who can check and correct the answers very well. Please check if the [solution] to the following question is correct. If the answer is not correct, point out the error step.\n'+'\nHuman: \n'+'[Question]: '+question+'\n[solution]: \n'+data[i]['output1'].strip()+'\n\nAssistant: \n'
    
    instruction=prompt
    step_check_prompt.append(instruction)
    i+=1

step_check_outputs = llm.generate(step_check_prompt, sampling_params_2)

i=0
k=0
correction_prompt=[]
need_correction_idx=[]
while i<len(data): 
    
    question=data[i]['question']
    
        
    step_check_output = step_check_outputs[i].outputs[0].text.replace('</s>','').replace('<unk>','')
    print(step_check_output)
    step_check=step_check_output.strip()
    data[i]['output2']=step_check
        
    if 'is wrong' in step_check or 'is incorrect' in step_check:
            
        data[i]['pred_wrong_step']=int(step_check[5])       
        need_correction_idx.append(i)
        #check='Step {} is wrong.'.format(j+1)
        check=step_check.split('\n')[-1]
        #instruction='System: \nYou are an AI assistant who can check and correct the answers very well. Please start from the wrong step in the [original answer] as point out by the [check] and think step by step to get the correct answer. You should correct the error pointed out by the [check] in the [original answer]. Please keep your reasoning step close to the [original answer] if possible.\n'+'\nHuman: \n'+'[Question]: '+question+'\n[original answer]: \n'+data[i]['output1'].strip()+'\n[check]: \n'+check+'\n[correction]: \n'
        instruction="System: \nYou are an AI assistant who can check and correct the answers very well. Please correct the [original answer] of the [Question] and think step by step to get the correct answers. You should correct the error pointed out by the [check] in the [original answer].\n"+'\nHuman: \n'+'[Question]: '+question+'\n[original answer]: \n'+data[i]['output1'].strip()+'\n[check]: \n'+check
        '''
        for k in range(wrong_step-1):
            if k>=step_num-1:
                break
            instruction+='step {}: '.format(k+1)+original_output[k]+'\n'
        '''
                
        instruction+='\n\nAssistant: \n'
        correction_prompt.append(instruction)
    i+=1
    
correction_outputs = llm.generate(correction_prompt, sampling_params_3)
cnt=0
for i in need_correction_idx:
    correction_output = correction_outputs[cnt].outputs[0].text.replace('</s>','').replace('<unk>','')
    print(correction_output)
    correction=correction_output.strip()
    data[i]['output3']=correction
    cnt+=1

i=0
while i<len(data):
    
    new_line=json.dumps(data[i],ensure_ascii=False)
    output_file.write(new_line+'\n')
    i+=1
