import os
import concurrent.futures
import sys
from src import epClipper

''' 执行任务 '''


def thread_invoke(file_path, scene_path):
    # sys.stdout.write("文件全路径名称："+file_path+"\n")
    video_name = os.path.basename(file_path)
    video_path = os.path.dirname(file_path)
    sys.stdout.write("文件名称:" + video_name + "\n")
    sys.stdout.write("文件路径:" + video_path + "\n")
    # sys.stdout.write("根目录路径："+root_path+"\n")
    cut_scene_path = replace_first_directory(video_path, scene_path)
    sys.stdout.write("分割场景目录路径：" + cut_scene_path + "\n")
    invoker = epClipper.epClipper(clip_path=cut_scene_path, video_path=video_path)
    invoker.split_video(video_name)


''' 替换文件root路径 '''


def replace_first_directory(path, new_dir):
    # 验证路径是否有效
    names = path.split("\\")
    new_path = ""
    for index, name in enumerate(names):
        if index == 0:
            new_path += new_dir
        else:
            new_path += "\\" + name
    return new_path


''' 视频场景智能分割服务 '''


class CutServer:
    def __init__(self, video_path='video', clip_path='clip', max_workers=5):
        self.video_path = video_path
        self.max_workers = max_workers
        self.clip_path = clip_path

    ''' 创建目录'''

    def make_dirs(self):
        scene_dirs = []
        scene_dirs += [self.video_path]
        scene_dirs += [self.clip_path]
        for root, dirs, files in os.walk(self.video_path):
            for dir in dirs:
                scene_dirs += [os.path.join(replace_first_directory(root, self.clip_path), dir)]
        for path in scene_dirs:
            if not os.path.exists(path):
                os.makedirs(path)

    ''' 启动服务 '''

    def run(self):
        self.make_dirs()
        suffixes = ['.mp4', '.MP4', '.mkv', '.MKV', '.flv', '.FLV']
        file_path_list = []
        # 遍历文件
        for root, dirs, files in os.walk(self.video_path):
            for file in files:
                file_path = os.path.join(root, file)
                suffix = os.path.splitext(file_path)[-1]
                if suffix in suffixes:
                    file_path_list.append(file_path)
        # 线程池运行
        with concurrent.futures.ThreadPoolExecutor(self.max_workers) as executor:
            futures = [executor.submit(thread_invoke, file_path, self.clip_path) for file_path in file_path_list]
        for future in concurrent.futures.as_completed(futures):
            print(f"任务 {future.result()} 完成")
