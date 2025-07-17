import copy
import random
from openai import OpenAI
import pandas as pd
import os, sys

# 获取程序运行所在路径
if hasattr(sys, 'frozen'):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

# 设置不同AI模型
base_url = ''
model = ''
api_key_list = []
client = None


def get_files(folder):
    '''
    获取文件夹所有文件
    :param folder:
    :return:
    '''
    all_files = []
    for root, dirs, files in os.walk(folder):
        for name in files:
            full_path = os.path.join(root, name)
            all_files.append(full_path)
    return all_files

def get_json_content(response):
    '''
    提取JSON数据
    :param response:
    :return:
    '''
    start_idx = response.find("```json")
    if start_idx != -1:
        start_idx += 7
        response = response[start_idx:]

    end_idx = response.rfind("```")
    if end_idx != -1:
        response = response[:end_idx]

    json_content = response.strip()
    return json_content

def get_dict(value, temp=[]):
    '''处理JSON数据'''
    for _, key in value.items():
        if isinstance(key, dict):
            temp = get_dict(key, temp)
        if isinstance(key, list):
            for r in key:
                if isinstance(r, dict):
                    temp = get_dict(r, temp)
                else:
                    temp.append(r)
    return temp

def save_file(file_name, result, analysis):
    '''
    统计标签数据并写入文件
    :param file_name:
    :param result:
    :param analysis:
    :return:
    '''
    # 数据处理
    column_name = {}
    if analysis:
        for a in analysis:
            if a[0] not in column_name.keys():
                column_name[a[0]] = [a[1]]
            else:
                column_name[a[0]].append(a[1])
    analysis_df = pd.DataFrame(columns=['sentiment', 'label', 'number', 'keyword'])
    for key, value in column_name.items():
        sentiment = '正面' if '正面' in key else '负面'
        new_row = {'sentiment': sentiment, 'label': str(key).split(']')[-1], 'number': len(value), 'keyword': '\n'.join(value)}
        analysis_df = analysis_df._append(new_row, ignore_index=True)
    # 写入文件
    result_path = f'{application_path}/result'
    if not os.path.exists(result_path):
        os.makedirs(result_path)
    with pd.ExcelWriter(f"{result_path}/{file_name}") as writer:
        result.to_excel(writer, sheet_name='Sheet1', index=False)
        analysis_df.to_excel(writer, sheet_name='Sheet2', index=False)

def ai_analyse(comment, labels):
    '''
    根据标签系统分析当前评论符合的标签
    :param comment:
    :param labels:
    :return:
    '''
    print('******ai_analyse******')
    prompt = f"""请基于评论标签体系进行标签分析，标签体系为： ### : {labels}, ### , 
要求：当评论满足标签则记录下标签，从评论中找出满足的关键词句，当评论不符合标签则去掉标签。按评论内容是否正面评论还是反面评论，标记形如：’[正面]标签’、‘[负面]标签‘作为标签。 格式返回为原来的标签体系结构，数据类型为json格式，格式如下：
```json
{{
"人群与场景": {{
	"用户需求与痛点-使用场景": [
		["[正面]工作场合佩戴", "适合上班佩戴"],
		["[正面]送礼对象","孩子很喜欢"],
		["[正面]视频推荐吸引","在tiktok看到"],
		["[正面]购买多次", "老顾客"],
		["[正面]更小码需求","尺寸有点大"]
	],
}},
....
}}
```  
以下是评论内容： 
##
   {comment}
## """
    result = ''
    global client
    for _ in range(len(api_key_list)+1):
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                timeout=60  # 添加超时设置
            )
            result = completion.choices[0].message.content
            break
        except:
            api_key = client.api_key
            api_key_list.remove(api_key)
            print(f'移除api_key：{api_key}')
            client = OpenAI(
                base_url=base_url,
                api_key=random.choice(api_key_list),
            )
            print(f'更换api_key：{client.api_key}')
    return result

def run_analyse(file_path):
    '''
    读取文件夹所有文件，并对xlsx读取
    获取xlsx里面包含content的每一行数据
    对每一行数据的评论内容调用ai_analyse()进行分析
    将分析结果写入数组，最后写入新的excel文件
    :param file_path:
    :return:
    '''
    if not os.path.exists(f'{application_path}/label.txt'):
        print('please set label.txt')
    else:
        if not os.path.exists(f'{application_path}/api.txt'):
            print('please set api.txt')
        else:
            f = open(f'{application_path}/api.txt', 'r', encoding='utf-8')
            api_info = f.read()
            f.close()
            global base_url, model, api_key_list, client
            for a in api_info.split('\n'):
                if 'base_url' in a:
                    base_url = a.replace('base_url', '').replace('=', '').strip()
                if 'model' in a:
                    model = a.replace('model', '').replace('=', '').strip()
                if 'api_key' in a:
                    api_key_list = a.replace('api_key', '').replace('=', '').strip().split(',')
                    api_key_list = [k.strip() for k in api_key_list]
            if base_url and model and api_key_list:
                client = OpenAI(
                    base_url=base_url,
                    api_key=random.choice(api_key_list),
                )
                all_files = get_files(file_path)
                f = open(f'{application_path}/label.txt', 'r', encoding='utf-8')
                labels = f.read()
                f.close()
                for file in all_files:
                    if '.xlsx' in file:
                        comment_analysis = []
                        file_name = os.path.basename(file)
                        content_column = ''
                        df = pd.read_excel(file)
                        # 获取列名
                        for column_name in df.columns:
                            if 'content' in column_name:
                                content_column = column_name
                        if not content_column:
                            continue
                        # 遍历每一行数据的评论内容
                        for index, row in df.iterrows():
                            comment = row[content_column]
                            if comment:
                                # AI分析
                                res = ai_analyse(comment, labels)
                                try:
                                    res_str = get_json_content(res)
                                    res_json = eval(res_str)
                                    print(res_json)
                                    # 提取分析内容并写入数组result
                                    temp = get_dict(res_json, [])
                                    comment_analysis += copy.deepcopy(temp)
                                    for i, t in enumerate(temp):
                                        if isinstance(t, list):
                                            t = ','.join(t)
                                        df.loc[index, f"label{i}"] = t
                                except:
                                    pass
                        # 保存新的excel文件
                        print(comment_analysis)
                        result_file = save_file(file_name, df, comment_analysis)
                        print(f"analysis result: {result_file}")
            else:
                print("api.txt's setting is incorrect")


if __name__ == '__main__':
    run_analyse(f'{application_path}/data')