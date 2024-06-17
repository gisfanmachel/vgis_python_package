# -*- coding: utf-8 -*-
import os

import cv2  ##加载OpenCV模块


class VideoOperator:
    def __init__(self):
        pass

    # 视频转图片
    def video2frames(self, pathIn='',
                     pathOut='',
                     only_output_video_info=False,
                     extract_time_points=None,
                     initial_extract_time=0,
                     end_extract_time=None,
                     extract_time_interval=-1,
                     output_prefix='frame',
                     jpg_quality=100,
                     isColor=True):
        '''
        pathIn：视频的路径，比如：F:\python_tutorials\test.mp4
        pathOut：设定提取的图片保存在哪个文件夹下，比如：F:\python_tutorials\frames1\。如果该文件夹不存在，函数将自动创建它
        only_output_video_info：如果为True，只输出视频信息（长度、帧数和帧率），不提取图片
        extract_time_points：提取的时间点，单位为秒，为元组数据，比如，(2, 3, 5)表示只提取视频第2秒， 第3秒，第5秒图片
        initial_extract_time：提取的起始时刻，单位为秒，默认为0（即从视频最开始提取）
        end_extract_time：提取的终止时刻，单位为秒，默认为None（即视频终点）
        extract_time_interval：提取的时间间隔，单位为秒，默认为-1（即输出时间范围内的所有帧）
        output_prefix：图片的前缀名，默认为frame，图片的名称将为frame_000001.jpg、frame_000002.jpg、frame_000003.jpg......
        jpg_quality：设置图片质量，范围为0到100，默认为100（质量最佳）
        isColor：如果为False，输出的将是黑白图片
        '''

        cap = cv2.VideoCapture(pathIn)  ##打开视频文件
        n_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  ##视频的帧数
        fps = cap.get(cv2.CAP_PROP_FPS)  ##视频的帧率
        dur = n_frames / fps  ##视频的时间

        ##如果only_output_video_info=True, 只输出视频信息，不提取图片
        if only_output_video_info:
            print('only output the vgis_video information (without extract frames)::::::')
            print("Duration of the vgis_video: {} seconds".format(dur))
            print("Number of frames: {}".format(n_frames))
            print("Frames per second (FPS): {}".format(fps))

            ##提取特定时间点图片
        elif extract_time_points is not None:
            if max(extract_time_points) > dur:  ##判断时间点是否符合要求
                raise NameError('the max vgis_datetime point is larger than the vgis_video duration....')
            try:
                os.mkdir(pathOut)
            except OSError:
                pass
            success = True
            count = 0
            while success and count < len(extract_time_points):
                cap.set(cv2.CAP_PROP_POS_MSEC, (1000 * extract_time_points[count]))
                success, image = cap.read()
                if success:
                    if not isColor:
                        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  ##转化为黑白图片
                    print('Write a new frame: {}, {}th'.format(success, count + 1))
                    cv2.imwrite(os.path.join(pathOut, "{}_{:06d}.jpg".format(output_prefix, count + 1)), image,
                                [int(cv2.IMWRITE_JPEG_QUALITY), jpg_quality])  # save frame as JPEG vgis_file
                    count = count + 1

        else:
            ##判断起始时间、终止时间参数是否符合要求
            if initial_extract_time > dur:
                raise NameError('initial extract vgis_datetime is larger than the vgis_video duration....')
            if end_extract_time is not None:
                if end_extract_time > dur:
                    raise NameError('end extract vgis_datetime is larger than the vgis_video duration....')
                if initial_extract_time > end_extract_time:
                    raise NameError('end extract vgis_datetime is less than the initial extract vgis_datetime....')

            ##时间范围内的每帧图片都输出
            if extract_time_interval == -1:
                if initial_extract_time > 0:
                    cap.set(cv2.CAP_PROP_POS_MSEC, (1000 * initial_extract_time))
                try:
                    os.mkdir(pathOut)
                except OSError:
                    pass
                print('Converting a vgis_video into frames......')
                if end_extract_time is not None:
                    N = (end_extract_time - initial_extract_time) * fps + 1
                    success = True
                    count = 0
                    while success and count < N:
                        success, image = cap.read()
                        if success:
                            if not isColor:
                                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                            print('Write a new frame: {}, {}/{}'.format(success, count + 1, n_frames))
                            cv2.imwrite(os.path.join(pathOut, "{}_{:06d}.jpg".format(output_prefix, count + 1)), image,
                                        [int(cv2.IMWRITE_JPEG_QUALITY), jpg_quality])  # save frame as JPEG vgis_file
                            count = count + 1
                else:
                    success = True
                    count = 0
                    while success:
                        success, image = cap.read()
                        if success:
                            if not isColor:
                                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                            print('Write a new frame: {}, {}/{}'.format(success, count + 1, n_frames))
                            cv2.imwrite(os.path.join(pathOut, "{}_{:06d}.jpg".format(output_prefix, count + 1)), image,
                                        [int(cv2.IMWRITE_JPEG_QUALITY), jpg_quality])  # save frame as JPEG vgis_file
                            count = count + 1

            ##判断提取时间间隔设置是否符合要求
            elif extract_time_interval > 0 and extract_time_interval < 1 / fps:
                raise NameError('extract_time_interval is less than the frame vgis_datetime interval....')
            elif extract_time_interval > (n_frames / fps):
                raise NameError('extract_time_interval is larger than the duration of the vgis_video....')

            ##时间范围内每隔一段时间输出一张图片
            else:
                try:
                    os.mkdir(pathOut)
                except OSError:
                    pass
                print('Converting a vgis_video into frames......')
                if end_extract_time is not None:
                    N = (end_extract_time - initial_extract_time) / extract_time_interval + 1
                    success = True
                    count = 0
                    while success and count < N:
                        cap.set(cv2.CAP_PROP_POS_MSEC,
                                (1000 * initial_extract_time + count * 1000 * extract_time_interval))
                        success, image = cap.read()
                        if success:
                            if not isColor:
                                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                            print('Write a new frame: {}, {}th'.format(success, count + 1))
                            cv2.imwrite(os.path.join(pathOut, "{}_{:06d}.jpg".format(output_prefix, count + 1)), image,
                                        [int(cv2.IMWRITE_JPEG_QUALITY), jpg_quality])  # save frame as JPEG vgis_file
                            count = count + 1
                else:
                    success = True
                    count = 0
                    while success:
                        cap.set(cv2.CAP_PROP_POS_MSEC,
                                (1000 * initial_extract_time + count * 1000 * extract_time_interval))
                        success, image = cap.read()
                        if success:
                            if not isColor:
                                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                            print('Write a new frame: {}, {}th'.format(success, count + 1))
                            cv2.imwrite(os.path.join(pathOut, "{}_{:06d}.jpg".format(output_prefix, count + 1)), image,
                                        [int(cv2.IMWRITE_JPEG_QUALITY), jpg_quality])  # save frame as JPEG vgis_file
                            count = count + 1


def convert_video_to_images_test(video_operator):
    ##### 测试
    pathIn = 'D:\\vgis_video\\test.mp4'
    video_operator.video2frames(pathIn, only_output_video_info=True)

    pathOut = 'D:\\vgis_video\\frames1'
    video_operator.video2frames(pathIn, pathOut)
    #
    # pathOut = 'D:\\资料\\frames2'
    # 只提取了第1秒，第2秒和第5秒图片
    # video_operator.video2frames(pathIn, pathOut, extract_time_points=(1, 2, 5))
    #
    # pathOut = 'D:\\资料\\frames3'
    # 可以看到，1到3秒内的视频每隔0.5秒提取图片，共5张图片（分别为1s, 1.5s, 2s, 2.5s, 3s时刻的图片）
    # video_operator.video2frames(pathIn, pathOut,
    #              initial_extract_time=1,
    #              end_extract_time=3,
    #              extract_time_interval=0.5)
    #
    # pathOut = 'D:\\资料\\frames4'
    # video_operator.video2frames(pathIn, pathOut, extract_time_points=(0.3, 2), isColor=False)
    #
    # pathOut = 'D:\\资料\\frames5'
    # video_operator.video2frames(pathIn, pathOut, extract_time_points=(0.3, 2), jpg_quality=50)


# 主入口,进行测试
if __name__ == '__main__':
    try:
        video_operator = VideoOperator()

        convert_video_to_images_test(video_operator)

    except Exception as tm_exp:
        print("测试用例失败：{}".format(str(tm_exp)))
