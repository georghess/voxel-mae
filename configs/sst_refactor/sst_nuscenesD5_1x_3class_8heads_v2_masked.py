_base_ = [
    '../_base_/datasets/nus-3d-2sweep.py',
    '../_base_/schedules/cosine_2x.py',
    '../_base_/default_runtime.py',
]

voxel_size = (0.25, 0.25, 8)
window_shape = (16, 16, 1) # 12 * 0.32m
point_cloud_range = [-50, -50, -5, 50, 50, 3]
drop_info_training ={
    0:{'max_tokens':30, 'drop_range':(0, 30)},
    1:{'max_tokens':60, 'drop_range':(30, 60)},
    2:{'max_tokens':100, 'drop_range':(60, 100)},
    3:{'max_tokens':200, 'drop_range':(100, 200)},
    4:{'max_tokens':256, 'drop_range':(200, 100000)},
}
drop_info_test ={
    0:{'max_tokens':30, 'drop_range':(0, 30)},
    1:{'max_tokens':60, 'drop_range':(30, 60)},
    2:{'max_tokens':100, 'drop_range':(60, 100)},
    3:{'max_tokens':200, 'drop_range':(100, 200)},
    4:{'max_tokens':256, 'drop_range':(200, 100000)},
}
drop_info = (drop_info_training, drop_info_test)
shifts_list = [(0, 0), (window_shape[0]//2, window_shape[1]//2)]

model = dict(
    type='DynamicVoxelNet',

    voxel_layer=dict(
        voxel_size=voxel_size,
        max_num_points=-1,
        point_cloud_range=point_cloud_range,
        max_voxels=(-1, -1)
    ),

    voxel_encoder=dict(
        type='DynamicVFE',
        in_channels=4,
        feat_channels=[64, 128],
        with_distance=False,
        voxel_size=voxel_size,
        with_cluster_center=True,
        with_voxel_center=True,
        point_cloud_range=point_cloud_range,
        norm_cfg=dict(type='naiveSyncBN1d', eps=1e-3, momentum=0.01),
        return_gt_points=True
    ),

    middle_encoder=dict(
        type='SSTInputLayerV2Masked',
        window_shape=window_shape,
        sparse_shape=(400, 400, 1),
        shuffle_voxels=True,
        debug=True,
        drop_info=drop_info,
        pos_temperature=10000,
        normalize_pos=False,
    ),

    backbone = dict(
        type='SSTv2',
        d_model=[128,] * 1,
        nhead=[2, ] * 1,
        num_blocks=1,
        dim_feedforward=[256, ] * 1,
        output_shape=[400, 400],
        num_attached_conv=0,
        debug=True,
        masked=True
    ),

    neck=dict(
        type='SSTv2Decoder',
        d_model=[128,] * 6,
        nhead=[8, ] * 6,
        num_blocks=6,
        dim_feedforward=[256, ] * 6,
        output_shape=[400, 400],
        debug=True,
    ),

    bbox_head=dict(
        type='ReconstructionHead',
        in_channels=128,
        feat_channels=128,
        num_reg_points=10,
        only_masked=True,
    )
)

# runtime settings
runner = dict(type='EpochBasedRunner', max_epochs=12)
evaluation = dict(interval=12)

fp16 = dict(loss_scale=32.0)
workflow = [("train", 1), ("val", 1)]
data = dict(
    samples_per_gpu=1,
    workers_per_gpu=4,
)