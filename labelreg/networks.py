import tensorflow as tf
import labelreg.layers as layer
import labelreg.utils as util


def build_network(network_type, **kwargs):
    type_lower = network_type.lower()
    if type_lower == 'local':
        return LocalNet(**kwargs)
    elif type_lower == 'global':
        return GlobalNet(**kwargs)
    elif type_lower == 'composite':
        return CompositeNet(**kwargs)


class BaseNet:

    def __init__(self, minibatch_size, image_moving, image_fixed):
        self.minibatch_size = minibatch_size
        self.image_size = image_fixed.shape.as_list()[1:4]
        self.grid_ref = util.get_reference_grid(self.image_size)
        self.grid_warped = tf.zeros_like(self.grid_ref)  # initial zeros are safer for debug
        self.image_moving = image_moving
        self.image_fixed = image_fixed
        self.input_layer = tf.concat([layer.resize_volume(image_moving, self.image_size), image_fixed], axis=4)

    def warp_image(self, input_):
        if input_ is None:
            input_ = self.image_moving
        return util.resample_linear(input_, self.grid_warped)


class LocalNet(BaseNet):

    def __init__(self, ddf_levels=None, **kwargs):
        BaseNet.__init__(self, **kwargs)
        # defaults
        self.ddf_levels = [0, 1, 2, 3, 4] if ddf_levels is None else ddf_levels
        self.num_channel_initial = 32
        #32,64,128,256,512
        nc = [int(self.num_channel_initial*(2**i)) for i in range(5)]
        h0, hc0 = layer.downsample_resnet_block(self.input_layer, 2, nc[0], k_conv0=[7, 7, 7], name='local_down_0')
        h1, hc1 = layer.downsample_resnet_block(h0, nc[0], nc[1], name='local_down_1')
        h2, hc2 = layer.downsample_resnet_block(h1, nc[1], nc[2], name='local_down_2')
        h3, hc3 = layer.downsample_resnet_block(h2, nc[2], nc[3], name='local_down_3')

        #这个代码是对应文章中 fig.4 中的哪个卷积块？
        hm = [layer.conv3_block(h3, nc[3], nc[4], name='local_deep_4')]

        min_level = min(self.ddf_levels)
        hm += [layer.upsample_resnet_block(hm[0], hc3, nc[4], nc[3], name='local_up_3')] if min_level < 4 else []
        hm += [layer.upsample_resnet_block(hm[1], hc2, nc[3], nc[2], name='local_up_2')] if min_level < 3 else []
        hm += [layer.upsample_resnet_block(hm[2], hc1, nc[2], nc[1], name='local_up_1')] if min_level < 2 else []
        hm += [layer.upsample_resnet_block(hm[3], hc0, nc[1], nc[0], name='local_up_0')] if min_level < 1 else []

        self.ddf = tf.reduce_sum(tf.stack([layer.ddf_summand(hm[4-idx], nc[idx], self.image_size, name='sum_%d' % idx)
                                           for idx in self.ddf_levels],
                                          axis=5), axis=5)
        self.grid_warped = self.grid_ref + self.ddf#grid_ref是标准的mesh_grid，而ddf是两张图片的变化量


class GlobalNet(BaseNet):

    def __init__(self, **kwargs):
        BaseNet.__init__(self, **kwargs)
        # defaults
        self.num_channel_initial_global = 8
        self.transform_initial = [1., 0., 0., 0., 0., 1., 0., 0., 0., 0., 1., 0.]

        nc = [int(self.num_channel_initial_global * (2 ** i)) for i in range(5)]
        h0, hc0 = layer.downsample_resnet_block(self.input_layer, 2, nc[0], k_conv0=[7, 7, 7], name='global_down_0')
        h1, hc1 = layer.downsample_resnet_block(h0, nc[0], nc[1], name='global_down_1')
        h2, hc2 = layer.downsample_resnet_block(h1, nc[1], nc[2], name='global_down_2')
        h3, hc3 = layer.downsample_resnet_block(h2, nc[2], nc[3], name='global_down_3')
        h4 = layer.conv3_block(h3, nc[3], nc[4], name='global_deep_4')
        theta = layer.fully_connected(h4, 12, self.transform_initial, name='global_project_0')

        self.grid_warped = util.warp_grid(self.grid_ref, theta)
        self.ddf = self.grid_warped - self.grid_ref


class CompositeNet(BaseNet):

    def __init__(self, **kwargs):
        BaseNet.__init__(self, **kwargs)
        # defaults
        self.ddf_levels = [0]

        global_net = GlobalNet(**kwargs)
        local_net = LocalNet(minibatch_size=self.minibatch_size,
                             image_moving=global_net.warp_image(),
                             image_fixed=self.image_fixed,
                             ddf_levels=self.ddf_levels)

        self.grid_warped = global_net.grid_warped + local_net.ddf
        self.ddf = self.grid_warped - self.grid_ref
