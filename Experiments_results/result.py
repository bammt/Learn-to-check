import re
import json
def test_answer(pred_str, ans_str):
    pattern = '[0-9,]*\.?[0-9]+'
    pred = re.findall(pattern, pred_str)
    if(len(pred) >= 1):
        # print(pred_str)
        pred = pred[-1]
        gold = re.findall(pattern, ans_str)
        # print(ans_str)
        gold = gold[-1]
        pred=float(pred.replace(',',''))
        gold=float(gold.replace(',',''))
        #print(pred,gold)
        return ['have_answer',abs(pred - gold)<0.001,pred]
    
    else:
        #print(pred_str)
        return ['no_answer',False,pred]

def parse_pred_ans(filename):
    file=open(filename,"r", encoding='UTF-8')
    
    num_q, acc_1,acc_2 = 0, 0, 0
    num_c_c,num_c_w,num_w_c,num_w_w=0,0,0,0
    num_c2c,num_c2w,num_w2c=0,0,0
    no_change=0
    find_step=0
    while  True:
        # Get next line from file
        line  =  file.readline()
        
        if  not  line:
            break 
        line=json.loads(line)
        
        gold_answer=str(line['answer'])
        pred_answer1=str(line['output1'])
        if 'output3' in line.keys():
            pred_answer2=str(line['output3'])
            
        else:
            pred_answer2=''
        
        num_q+=1
        pred_1=test_answer(pred_answer1,gold_answer)
        pred_2=test_answer(pred_answer2,gold_answer)
        pred_3=test_answer(pred_answer1+pred_answer2,gold_answer)
        if  pred_1[1]:
            acc_1+=1
            if pred_2[0]=='no_answer':
                num_c_c+=1
            else:
                num_c_w+=1
                if pred_2[1]:
                    num_c2c+=1
                else:
                    num_c2w+=1
        else:
            if pred_2[0]=='no_answer':
                num_w_c+=1
            else:
                num_w_w+=1 
                if pred_2[1]:
                    num_w2c+=1
        if pred_3[1]:
            acc_2+=1  
        if pred_1[2]==pred_2[2]:
            no_change+=1   
        if 'wrong_step' in line.keys():
            if 'pred_wrong_step' in line.keys() and line['pred_wrong_step']==line['wrong_step']:
                find_step+=1
    print('direct: num_q %d correct %d ratio %.4f' % (num_q, acc_1, float(acc_1 / num_q)))
    print('self_correction: num_q %d correct %d ratio %.4f' % (num_q, acc_2, float(acc_2 / num_q)))
    print('c_c: num_c_c %d ratio %.4f' % (num_c_c, float(num_c_c / num_q)))
    print('c_w: num_c_w %d ratio %.4f' % (num_c_w, float(num_c_w / num_q)))
    print('w_c: num_w_c %d ratio %.4f' % (num_w_c, float(num_w_c / num_q)))
    print('w_w: num_w_w %d ratio %.4f' % (num_w_w, float(num_w_w / num_q)))
    print('c2c: num_c2c %d' % num_c2c )
    print('c2w: num_c2w %d' % num_c2w )
    print('w2c: num_w2c %d' % num_w2c )
    print('check_correct_rate: total: %.4f correct: %.4f wrong: %.4f' % (float((num_c_c+num_w_w)/num_q), float(num_c_c/acc_1),float(num_w_w/(num_q-acc_1))))
    print('rate_no_change: %.4f' %float(no_change / (num_c_w+num_w_w)))
    print('find_step: %.4f' %float(find_step))
parse_pred_ans("a.txt")