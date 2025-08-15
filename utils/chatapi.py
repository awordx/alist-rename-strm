import http.client
import json
import configparser
from utils.log_utils import logger
import codecs
import ast
import os
from utils.log_utils import config_path
def read_config(config_path):
    config = configparser.ConfigParser()
    with codecs.open(config_path, 'r', encoding='utf-8') as f:
        config.read_file(f)
    return config
def ai_rename(series_names_list):
    series_names_list = str(series_names_list)
    conn = http.client.HTTPSConnection("api.chatanywhere.tech")
    payload = json.dumps({
       "model": "gpt-4o-mini",
       "messages": [
          {
             "role": "system",
             "content": "你现在是一个影视专家，见过各式各样的剧集名字，复杂的，简单的，杂乱的你都见过，但你都能准确识别剧集的集数，要满足一下要求"
                        "1.我发你一个剧集的名字列表，你要返回对应剧集的数字集数，同样以列表的形式返回,返回的集数要和发你的对应上,例如发你[1.mkv,2.mp4]，要返回[1,2]"
                        "2.如果有些集数你也不知道怎么命名就返回null（但是你要用尽全力思考并反思后确定这个文件名确实没办法提取集数）,例如发你[spares.mkv,google.mp4]，有无剧集无数字，无法命名，要返回[null,null]"
                        "3.如果名字中含有这些{(S\d+E\d+|r'OVA\d*|'NCED\d*|'Nced\d*|'nced\d*|'NCOP\d*|'Ncop\d*|'SP\d*|r'Sp\d*|r'OAD\d*|r'Oad\d*|r'sp\d*)}正则表达式匹配的字符，则相应名字直接返回null"
                        "不被正则表达式识别则回复正常集数，例如[ova1.mp4, ova2.mp4,3.mp4]则返回[null,null,3]"
                        "4.如果有的名字重复，要返回重复的名字，但是列表中的每个名字都要返回，例如[1.mp4,1.mkv,2.mkv]，要返回[1,1,2]"
                        "5.命名的时候不要被sx给迷惑，例如[s0 8.mp4,8.mp4,s2 8]则不用管s后面的字符，返回[8,8,8]"
                        "6.这是最重要的！！！如果你发给我的列表只含有一两个null，极可能是你命名错了，你要再仔细检查几遍再发给我，确保你没有命名错误"
          },
          {
             "role": "user",
             "content": series_names_list
          }
       ]
    })
    config = read_config(config_path)
    chat_api = config['user_config']['chat_api']
    headers = {
       'Authorization': f'Bearer {chat_api}',
       'Content-Type': 'application/json'
    }
    conn.request("POST", "/v1/chat/completions", payload, headers)
    res = conn.getresponse()
    # 检查状态码
    if res.status != 200:
        logger.info(f"⊗请求失败：{res.status}，原因：{res.reason}")
        logger.info(f"使用普通办法命名")
        return None

    data = res.read()
    data = json.loads(data.decode("utf-8"))
    content = data['choices'][0]['message']['content']
    logger.info(f"🤖ai命名列表：{content}")
    try:
        result_list = json.loads(content)
    except json.JSONDecodeError as e:
        logger.info("ai命名中含有None值，使用普通办法命名")
        result_list = None
    return result_list
def ai_rename_anime_movie(series_name):
    parent = os.path.dirname(series_name)
    series_name = os.path.basename(series_name)

    series_name = str(series_name)
    conn = http.client.HTTPSConnection("api.chatanywhere.tech")
    payload = json.dumps({
       "model": "gpt-4o-mini",
       "messages": [
          {
             "role": "system",
             "content": "你现在是一个影视专家，见过各式各样的夹杂广告的剧集名字，复杂的，简单的，杂乱的你都见过，但你都能准确识别剧集的真实名字，要满足以下要求"
                        "1.我发你一个字符串，里面包含广告年份还有真正的剧集名字，然后你要根据你的经验还有网络知识来识别出真正的剧集名字，并把剧集名字的字符串发送给我"
                        "2.同时你也会生成一个置信度，如果你百分之百确定你提取的剧集名字是正确的，置信度就写1，如果不太确定就根据你的经验写，小于1的其他数字"
                        "3.将真正的剧集名字和执行度放到一个列表里面给我，只要这个列表，其他任何话都不要回复，列表的形状为第一个元素使剧集名字，为字符串格式，第二个元素"
                        "是置信度，为浮点数格式"
                        "4.例如有一个夹杂广告的剧集为'梦幻天龙.2008.七龙珠第一季'，你就要返回['七龙珠',1]，当然这个置信度由你自己来决定"
                        "5.这是最重要的！！！你要再仔细检查几遍再发给我，确保你没有命名错误"
          },
          {
             "role": "user",
             "content": series_name
          }
       ]
    })
    config = read_config('config/config_test.ini')
    chat_api = config['user_config']['chat_api']
    headers = {
       'Authorization': f'Bearer {chat_api}',
       'Content-Type': 'application/json'
    }
    conn.request("POST", "/v1/chat/completions", payload, headers)
    res = conn.getresponse()
    # 检查状态码
    if res.status != 200:
        logger.info(f"⊗请求失败：{res.status}，原因：{res.reason}")
        logger.info(f"使用普通办法命名")
        return None

    data = res.read()
    data = json.loads(data.decode("utf-8"))
    content = data['choices'][0]['message']['content']
    result = ast.literal_eval(content)
    logger.info(f"重命名：{series_name}->{result[0]}，置信度：{result[1]*100}%")
    new_path = parent+'/'+result[0]
    return new_path
if __name__ == '__main__':
    series_names_list =['海绵宝宝第1季 第15集_896x680_H265_23.15_124.39MB.mp4', '.海绵宝宝第1季 第9集_896x688_H265_22.34_121.35MB.mp4', '海绵宝宝第1季 第8集_896x680_H265_22.35_118.32MB.mp4', '海绵宝宝第1季 第7集_896x680_H265_22.35_119.96MB.mp4', '海绵宝宝第1季 第5集_896x680_H265_22.32_118.80MB.mp4', '.海绵宝宝第1季 第4集_896x672_H265_22.35_120.75MB.mp4', '.海绵宝宝第1季 第3集_896x672_H265_22.36_117.86MB.mp4', '.海绵宝宝第1季 第2集_896x672_H265_22.35_118.96MB.mp4', '.海绵宝宝第1季 第19集_896x680_H265_22.50_122.15MB.mp4', '.海绵宝宝第1季 第18集_896x672_H265_22.41_121.81MB.mp4', '.海绵宝宝第1季 第17集_896x680_H265_22.36_117.48MB.mp4', '.海绵宝宝第1季 第16集_896x680_H265_22.50_122.29MB.mp4', '.海绵宝宝第1季 第13集_896x672_H265_22.34_117.98MB.mp4', '.海绵宝宝第1季 第10集_896x672_H265_22.34_120.03MB.mp4', '.海绵宝宝 第1季 第1集_896x672_H265_22.46_115.51MB.mp4', '.海绵宝宝第1季 第20集_896x672_H265_23.24_125.91MB.mp4', '.海绵宝宝第1季 第14集_896x680_H265_23.04_124.70MB.mp4']
    name_list = ai_rename(series_names_list)
    logger.info(name_list)
    pass