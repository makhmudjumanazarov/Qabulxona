from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
import pandas as pd
import re


def numToWords(num,join=True):
    num = int(float(num))
    units = ["","bir","ikki",'uch',"toʻrt",'besh','olti','yetti','sakkiz',"toʻqqiz"]
    tens = ['',"oʻn",'yigirma',"oʻttiz",'qirq','ellik','oltmish','yetmish', 'sakson',"toʻqson"]
    thousands = ['','ming','million','milliard','trillion','kvadrillion','kvintilion','sekstilion','septillion','oktilion', 'nonillion','dekillion','undekillion','duodekillion', 'tredekillion','quattuordekillion','sexdekillion', 'septendekillion','oktodekillion','novemdekillion', 'vigintillion', 'unvigintillion','duovigintillion', 'trevigintillion', 'quattourvigintillion' , 'quinvigintillion', 'hexvigintillion', 'septenvigintillion', 'octovigintillion', 'novemvigintillion', 'trigintillion', 'untrigintillion', 'duotrigintillion', 'googol']
    words = []
    if num==0: words.append('nol')
    else:
        numStr = '%d'%num
        numStrLen = len(numStr)
        
        groups = (numStrLen+2)//3
        numStr = numStr.zfill(groups*3)
        for i in range(0,groups*3,3):
            h,t,u = int(numStr[i]),int(numStr[i+1]),int(numStr[i+2])
            g = groups-(i//3+1)
            if h>=1:
                words.append(units[h])
                words.append('yuz')
            if t>1:
                words.append(tens[t])
                if u>=1: words.append(units[u])
            elif t==1:
                if u>=1: words.append( tens[1]+" " + units[u])
                else: words.append(tens[t])
            else:
                if u>=1: words.append(units[u])
            if (g>=1) and ((h+t+u)>0): words.append(thousands[g]+' ')
    if join: return ' '.join(words)
    return words

def is_number(s):
    try:
        if '.' in s:
            return float(s)
        elif ',' in s:
            return  float(s.split(',')[0] + '.'+ s.split(',')[1])
        else:
            return int(s)
    except ValueError:
        return s


def text_ichida_(str_text):
    for i in range(len(str_text)):
        if isinstance(is_number(str_text[i]), float):
            if is_number(str_text[i]) > 0:
                k1 = str(is_number(str_text[i])).split('.')
                str_text[i] = f"{numToWords(int(k1[0]))} butun {numToWords(int(k1[1]))}"
            elif is_number(str_text[i]) < 0:
                k2 = str(is_number(str_text[i]))[1:].split('.')
                str_text[i] = f" minus {numToWords(int(k2[0]))} butun {numToWords(int(k2[1]))}"
            elif is_number(str_text[i]) == 0.0:
                k3 = str(is_number(str_text[i])).split('.')
                str_text[i] = f"{numToWords(int(k3[0]))} butun {numToWords(int(k3[1]))}"
        elif isinstance(is_number(str_text[i]), int):
            if is_number(str_text[i]) > 0:
                str_text[i] = numToWords(is_number(str_text[i]))
            else: 
                str_text[i] = f" minus {numToWords(abs(is_number(str_text[i])))}"
    return str_text

def raqamchi_(df):
    df['content'] = df['content'].map(lambda x: " ".join(text_ichida_(x.split())))
    return df

def regex_for_numbers_(df):
    df['content']=df['content'].map(lambda x: x.lower())
    df['content']=df['content'].map(lambda x: re.sub(r"(ʻ|‘|`|’|')","ʼ", x))
    df['content']=df['content'].map(lambda x: re.sub(r"(\d)(ʼ|ʻ)",r"\1 ", x))
    df['content']=df['content'].map(lambda x: re.sub(r" (ʼ|ʻ) ",r" ", x))
    df['content']=df['content'].map(lambda x: re.sub(r"(o|g)ʼ",r"\1ʻ", x))
    df['content']=df['content'].map(lambda x: re.sub(r'([a-z]+)-([0-9]+)(\w*)', r'\1 \2 \3', x))
    df['content']=df['content'].map(lambda x: re.sub(r'(\d+)\.([a-z]+)', r'\1 . \2', x)) 
    df['content']=df['content'].map(lambda x: re.sub(r'([a-z]+)-([a-z]+)(\d+)', r'\1 - \2 \3 ', x)) 
    df['content']=df['content'].map(lambda x: re.sub(r'([a-z]+)-(\d{1,9})-([a-z]+)', r'\1 - \2 - \3', x)) 
    df['content']=df['content'].map(lambda x: re.sub(r'(\d)-(\d)-(\d)-(\d)', r'\1 - \2 - \3 - \4', x))
    df['content']=df['content'].map(lambda x: re.sub(r'(\D)(\d{4})(\d{4})(\D)', r"\1 \2 - \3 \4 yil oraligʻida ", x)) 
    df['content']=df['content'].map(lambda x: re.sub(r'(\")([0-9]+)', r'\1 \2 ', x))
    df['content']=df['content'].map(lambda x: re.sub(r'([0-9]+)-([0-9]+)-([0-9]+)', r'\1 - \2 - \3 ', x)) 
    df['content']=df['content'].map(lambda x: re.sub(r'([0-9])+-([0-9]+)-([a-z]+)', r'\1 inchi \2 inchi \3', x)) 
    df['content']=df['content'].map(lambda x: re.sub(r'([a-z]+\.)([0-9]+)-([0-9]+)(\.)([a-z]+)', r'\1 \2 - \3 \4 \5', x)) 
    df['content']=df['content'].map(lambda x: re.sub(r'([0-9]+)-([0-9]+)([a-z]+)', r'\1 - \2 \3', x)) 
    df['content']=df['content'].map(lambda x: re.sub(r'([0-9]+)-([0-9]+)', r'\1 inchi \2 inchi', x)) 
    df['content']=df['content'].map(lambda x: re.sub(r'([a-z]+\.)([0-9]+)(\.)', r'\1 \2 \3 ', x)) 
    df['content']=df['content'].map(lambda x: re.sub(r'([a-z]+\.)([0-9]+)', r'\1 \2 ', x)) 
    df['content']=df['content'].map(lambda x: re.sub(r'([a-z]+)([0-9]+)([a-z]+)', r' ', x))
    df['content']=df['content'].map(lambda x: re.sub(r'([0-9]+)-([a-z]+)', r'\1 inchi \2', x))
    df['content']=df['content'].map(lambda x: re.sub(r'([a-z]+)([0-9]+)', r'\1 \2', x))
    df['content']=df['content'].map(lambda x: re.sub(r'([0-9]+)([a-z]+)', r'\1 \2', x))
    df['content']=df['content'].map(lambda x: re.sub(r'([0-9]+)(\’[a-z]+)', r'\1 \2', x))
    df['content']=df['content'].map(lambda x: re.sub(r'([0-9]+)(\-)', r'\1 inchi \2', x))
    
    df['content']=df['content'].map(lambda x: re.sub(r'х', r'x', x))
    df['content']=df['content'].map(lambda x: re.sub(r'%', r' foiz', x))
    
    df['content']=df['content'].map(lambda x: re.sub(r'[^a-z0-9ʼʻ]', r' ', x))
    return df

def inchi_(df):
    df['content'] = df['content'].map(lambda x: re.sub(r"  inchi",r'inchi' , x))
    df['content'] = df['content'].map(lambda x: re.sub(r" inchi",r'inchi' , x))
    df['content'] = df['content'].map(lambda x: re.sub(r'\d', r'', x))
    return df


inchi = FunctionTransformer(inchi_)
raqamchi = FunctionTransformer(raqamchi_)
regex_for_numbers = FunctionTransformer(regex_for_numbers_)

toza = Pipeline(
[
    ('regeex', regex_for_numbers),
    ('raqamchi', raqamchi),
    ('inchi', inchi)
])