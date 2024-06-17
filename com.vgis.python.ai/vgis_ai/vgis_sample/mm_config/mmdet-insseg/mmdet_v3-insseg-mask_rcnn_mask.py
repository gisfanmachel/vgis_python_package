_base_ = '../../../configs/mask_rcnn/mask-rcnn_r50-caffe_fpn_ms-poly-3x_coco.py'
data_root = './data/mmdet-insseg/airplane/'

# 非常重要
metainfo = {

    'classes': ('transportplane', 'fighter', 'helicopter', 'transport'),
    'palette': [(101, 205, 228), (240, 128, 128), (154, 205, 50), (34, 139, 34)]
}
num_classes = 4

# 训练 40 epoch
max_epochs = 140
# 训练单卡 bs= 16
train_batch_size_per_gpu = 16
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
load_from = './data/mmdet-insseg/mask_rcnn_r50_caffe_fpn_mstrain-poly_3x_coco_bbox_mAP-0.408__segm_mAP-0.37_20200504_163245-42aa3d00.pth'  # noqa

# model = dict(
# 考虑到数据集太小，且训练时间很短，我们把 backbone 完全固定
# 用户自己的数据集可能需要解冻 backbone
# backbone=dict(frozen_stages=4),
# 不要忘记修改 num_classes
# bbox_head=dict(dict(num_classes=num_classes)))
# 我们还需要更改 head 中的 num_classes 以匹配数据集中的类别数
# 目标检测  box_head, 实例分割 mask_head
# 如果数据集太小，可以将backbone完全固定，backbone=dict(frozen_stages=4)
model = dict(
    roi_head=dict(
        bbox_head=dict(num_classes=num_classes), mask_head=dict(num_classes=num_classes)))

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

# 默认的学习率调度器是 warmup 1000，但是 cat 数据集太小了，需要修改 为 30 iter
# param_scheduler = [
#     dict(
#         type='LinearLR',
#         start_factor=1.0e-5,
#         by_epoch=False,
#         begin=0,
#         end=1000),
#     dict(
#         type='CosineAnnealingLR',
#         eta_min=base_lr * 0.05,
#         begin=max_epochs // 2,  # max_epoch 也改变了
#         end=max_epochs,
#         T_max=max_epochs // 2,
#         by_epoch=True,
#         convert_to_iter_based=True),
# ]
optim_wrapper = dict(optimizer=dict(lr=base_lr))

# 第二 stage 切换 pipeline 的 epoch 时刻也改变了
# _base_.custom_hooks[1].switch_epoch = max_epochs - num_epochs_stage2

val_evaluator = dict(ann_file=data_root + 'val/annotation_coco.json')
test_evaluator = val_evaluator

# 一些打印设置修改
default_hooks = dict(
    checkpoint=dict(interval=5, max_keep_ckpts=2, save_best='auto'),  # 同时保存最好性能权重
    logger=dict(type='LoggerHook', interval=5))
train_cfg = dict(max_epochs=max_epochs, val_interval=5)
