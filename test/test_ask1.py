import requests

url = 'http://localhost:5000/ask'
questions = [
    '2019年第4期小客车指标申请的总人数和单位数是多少？',
    '审核通过的个人和单位新能源小客车指标申请的有效编码数量分别是多少？',
    '本期将配置的个人普通小客车指标数量是多少？',
    '单位普通小客车指标的配置数量又是多少？',
    '新能源小客车指标年度配额是否已经用尽？',
    '如果年度配额已用尽，审核通过的有效申请编码将如何轮候配置？',
    '指标配置工作结束后，申请人如何查询配置结果？',
    '除了在线查询，还有哪些方式可以查询当期配置结果？',
    '取得指标的个人和单位如何下载打印小客车配置指标确认通知书？',
    '如果需要到现场领取，需要携带哪些证件？',
    '本期有多少失信被执行人被限制参与小客车指标配置？',
    '如果申请人对被纳入失信被执行人名单有异议，应该如何查询和提出异议？',
    '本次通告的主办单位是哪个？',
    '如果需要联系相关部门，应该拨打哪个电话号码？'
]

# 打开一个文件用于写入
with open('responses.txt', 'w', encoding='utf-8') as file:
    for question in questions:
        data = {
            'query': question
        }
        response = requests.post(url, json=data)
        # 将问题和响应写入文件
        file.write(f"Question: {question}\n")
        file.write("Response: " + str(response.json()) + "\n\n")