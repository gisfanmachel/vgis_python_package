_base_ = '../../../configs/cascade_rcnn/faster-rcnn_x101-32x4d_fpn_ms-3x_coco.py'
data_root = './data/mmdet-insseg/airplane/'

# 非常重要
metainfo = {
    'classes': ('transportplane', 'fighter', 'helicopter', 'transport'),
    'palette': [(101, 205, 228), (240, 128, 128), (154, 205, 50), (34, 139, 34)]
}
num_classes = 4

# 训练 140 epoch
max_epochs = 140
# 训练单卡 bs= 16
# 这个跟显存大小有关系
train_batch_size_per_gpu = 12
# 可以根据自己的电脑修改
train_num_workers = 4

# 验证集 batch size 为 1
val_batch_size_per_gpu = 1
val_num_workers = 2

# RTMDet 训练过程分成 2 个 stage，第二个 stage 会切换数据增强 pipeline
# num_epochs_stage2 = 5

# batch 改变了，学习率也要跟着改变， 0.004 是 8卡x32 的学习率
base_lr = train_batch_size_per_gpu * 0.004 / (32 * 8)

# 采用 COCO 预训练权重
# mim download mmdet --config cascade-rcnn_r101_fpn_1x_coco --dest .
# 需要现手动下载
load_from = './data/mmdet-objdet/faster_rcnn_x101_32x4d_fpn_mstrain_3x_coco_20210524_124151-16b9b260.pth'  # noqa


model = dict(
    roi_head=dict(
        bbox_head=dict(num_classes=num_classes, type='Shared2FCBBoxHead')))

# 数据集不同，dataset 输入参数也不一样
train_dataloader = dict(
    batch_size=train_batch_size_per_gpu,
    num_workers=train_num_workers,
    pin_memory=False,
    dataset=dict(
        data_root=data_root,
        metainfo=metainfo,
        ann_file='train/annotation_coco.json',
        data_prefix=dict(img='train/')))

val_dataloader = dict(
    batch_size=val_batch_size_per_gpu,
    num_workers=val_num_workers,
    dataset=dict(
        metainfo=metainfo,
        data_root=data_root,
        ann_file='val/annotation_coco.json',
        data_prefix=dict(img='val/')))

test_dataloader = val_dataloader


optim_wrapper = dict(optimizer=dict(lr=base_lr))


val_evaluator = dict(ann_file=data_root + 'val/annotation_coco.json')
test_evaluator = val_evaluator

# 一些打印设置修改
default_hooks = dict(
    checkpoint=dict(interval=5, max_keep_ckpts=2, save_best='auto'),  # 同时保存最好性能权重
    logger=dict(type='LoggerHook', interval=5))
train_cfg = dict(max_epochs=max_epochs, val_interval=5)
