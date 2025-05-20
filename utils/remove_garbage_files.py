import os
def remove_garbage_files(files):
    # 创建一个字典来存储有效文件的基准名
    base_names = {}
    # 定义大写数字（中文）
    uppercase_numbers = '一二三四五六七八九十百千万'
    # 遍历文件名，提取基准名
    for file in files:
        base_name = os.path.splitext(file)[0]
        # 提取除大写数字和小写数字以外的字符作为基准名
        # filtered_base_name = ''.join(
        #     filter(lambda x: x not in uppercase_numbers and not x.isdigit(), base_name)).strip()
        filtered_base_name = base_name
        # 将有效的剧集文件存储在字典中
        if filtered_base_name:
            if filtered_base_name not in base_names:
                base_names[filtered_base_name] = []
            base_names[filtered_base_name].append(file)
    # 遍历基准名字典，保留每个基准名下的第一个文件，认为这个是有效的
    # 查找相同的字符并检查文件名
    common_substr = find_common_substrings_old(base_names)

    return common_substr


def find_common_substrings_old(base_names):
    # 获取所有字符串的列表
    strings = list(base_names.keys())

    if not strings:
        return []

    total_strings = len(strings)
    min_required = int(total_strings * 0.7)  # 至少需要70%的字符串

    # 用于存储公共子串和其出现的计数
    common_counts = {}

    # 遍历每对字符串，找到公共部分
    for i in range(total_strings):
        for j in range(i + 1, total_strings):
            common_substr = common_substring(strings[i], strings[j])
            if common_substr:
                if common_substr in common_counts:
                    common_counts[common_substr] += 1
                else:
                    common_counts[common_substr] = 1

    # 找到符合条件的公共子串
    filtered_dict = {k: v for k, v in common_counts.items() if k.strip()}
    for common_substr, count in filtered_dict.items():
        if count >= min_required:
            return common_substr  # 返回第一个符合条件的公共子串

    return None  # 如果没有找到符合条件的公共子串
def find_common_substrings(base_names):
    # 用于存储前缀和其出现次数的字典
    prefix_count = {}
    # 遍历文件名，提取前缀并统计
    for name in base_names:
        # 提取前缀（去掉最后的 '-thumb'）
        prefix = name.rsplit('-', 1)[0]  # 分割并取前半部分
        if prefix in prefix_count:
            prefix_count[prefix] += 1
        else:
            prefix_count[prefix] = 1
    # 找出重复的前缀
    duplicate_prefixes = [prefix for prefix, count in prefix_count.items() if count > 1]
    if duplicate_prefixes == []:
        duplicate_prefixes = None
    return duplicate_prefixes




def common_substring(str1, str2):
    # 找到两个字符串的最长公共子串
    len1, len2 = len(str1), len(str2)
    longest = 0
    ending_index = 0

    # 创建一个二维数组来存储公共长度
    dp = [[0] * (len2 + 1) for _ in range(len1 + 1)]

    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            if str1[i - 1] == str2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
                if dp[i][j] > longest:
                    longest = dp[i][j]
                    ending_index = i
            else:
                dp[i][j] = 0

    return str1[ending_index - longest:ending_index]


if __name__ == '__main__':
    pass