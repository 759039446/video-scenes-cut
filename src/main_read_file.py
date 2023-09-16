import os
import re
import subprocess
import pandas as pd
import ffmpeg


# 读取MP4时长
def read_mp4_duration(video_path):
    command = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of',
               'default=noprint_wrappers=1:nokey=1', video_path]
    result = subprocess.run(command, stdout=subprocess.PIPE)
    duration = float(result.stdout)
    return duration


# 如果封面不存在，创建封面
def crate_cover_if_not_exist(cover_real_path, video_sence_path):
    if os.path.exists(cover_real_path):
        return
    else:
        # 文件不存在
        if not os.path.exists(os.path.dirname(cover_real_path)):
            os.makedirs(os.path.dirname(cover_real_path))
        ffmpeg.input(video_sence_path, ss=0).output(cover_real_path, vframes=1).run()


def list_to_map(headers):
    map = {}
    i = 0
    for header in headers:
        map[header] = i
        i += 1
    return map


def read_excel_to_sql(file_directory):
    # 打开CSV文件
    df = pd.read_excel(file_directory)
    headerMap = list_to_map(df.columns.tolist())
    dataList = df.iloc
    sqlList = []
    for data in dataList:
        sql = "INSERT INTO douyin_video_basic (work_type, collection_time, account_uid, sec_uid, douyin_id, short_id, work_id, work_description, publish_time, account_nickname, account_signature, work_url, music_title, music_link, static_cover, dynamic_cover, tag1, tag2, tag3, likes_count, comments_count, favorites_count, shares_count) " + \
              "VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}');".format(
                  data[headerMap['作品描述']],
                  data[headerMap['采集时间']],
                  data[headerMap['账号UID']],
                  data[headerMap['SEC_UID']],
                  data[headerMap['抖音号']],
                  data[headerMap['SHORT_ID']],
                  data[headerMap['作品ID']],
                  data[headerMap['作品描述']],
                  data[headerMap['发布时间']],
                  data[headerMap['账号昵称']],
                  data[headerMap['账号签名']],
                  data[headerMap['作品地址']],
                  data[headerMap['音乐标题']],
                  data[headerMap['音乐链接']],
                  data[headerMap['静态封面']],
                  data[headerMap['动态封面']],
                  data[headerMap['TAG_1']],
                  data[headerMap['TAG_2']],
                  data[headerMap['TAG_3']],
                  data[headerMap['点赞数量']],
                  data[headerMap['评论数量']],
                  data[headerMap['收藏数量']],
                  data[headerMap['分享数量']])
        sqlList.append(sql)
    return sqlList


def read_excel_and_save(readDirectory, saveDirectory):
    sqlList = []
    for item_path in os.listdir(readDirectory):
        if "xlsx" in item_path:
            sqlList.extend(read_excel_to_sql(readDirectory + "\\" + item_path))
    basic_info_sql = "".join(sqlList)
    with open(saveDirectory, 'w', encoding='utf-8') as f:
        f.write(basic_info_sql)


def generate_page(directory, split_directory, result, clip_path):
    for item_path in os.listdir(directory):
        item_path = directory + "\\" + item_path
        if os.path.isdir(item_path):
            # 如果是一个文件夹，递归调用
            generate_page(item_path, split_directory, result,clip_path)
        else:
            path = item_path.replace(split_directory, "")

            format = re.findall(r'\.[^.]+$', path)[0][1:]
            duration = 0
            cover = ""
            cover_path = ""
            author = ""
            if (format == "mp4"):
                file_name = os.path.basename(item_path)
                publish_time = file_name[:19]
                duration = read_mp4_duration(item_path)
                cover = directory + "\\scene\\" + file_name.replace(".mp4", "-01.jpg")
                crate_cover_if_not_exist(cover, item_path)
                cover_path = cover.replace(split_directory, "")
                author = item_path.split(clip_path)[1].split("\\")[0]
                result.append(
                    "INSERT INTO `douyin_file_info`(`path`, `format`, `duration`, `cover_path`, `author`, `publish_time`) VALUES ('{}', '{}', '{}', '{}', '{}', '{}');".format(
                        path.replace("\\", "/"), format, duration, cover_path.replace("\\", "/"), author, publish_time))

            print(path, format, duration, cover, cover_path, author)


def main(clip_path):
    # 读取视频分镜文件并保存为sql
    directory = 'clip'

    saveFileInfoSqlPath = 'sql/douyin_file.sql'

    if not os.path.exists(os.path.dirname(saveFileInfoSqlPath)):
        os.makedirs(os.path.dirname(saveFileInfoSqlPath))
    result = []
    generate_page(directory, directory, result, clip_path)
    # 将数组转换为字符串
    file_info_sql = "".join(result)
    with open(saveFileInfoSqlPath, 'w', encoding='utf-8') as f:
        f.write(file_info_sql)

    downloaderDataPath = r'D:\py_code\TikTokDownloader\Data'
    saveBasicInfoSqlPath = './sql/douyin_video_basic.sql'
    read_excel_and_save(downloaderDataPath, saveBasicInfoSqlPath)
