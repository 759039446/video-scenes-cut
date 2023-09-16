from src import main_scene_cut
from src import main_read_file
import TikTokDownloader

if __name__ == '__main__':
    TikTokDownloader.TikTokDownloader().run()
    # 视频场景分剪 使用多线程的方式来提升速度
    cutServer = main_scene_cut.CutServer(video_path='video', clip_path='clip')
    cutServer.run()
    # 读取视频封面并保存到视频的目录的scene文件夹中
    main_read_file.main('clip')
