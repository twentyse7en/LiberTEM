import numpy as np

from libertem import masks
from .masks import SingleMaskAnalysis
from .helper import GeneratorHelper


class DiskTemplate(GeneratorHelper):

    short_name = "disk"
    api = "create_disk_analysis"

    def __init__(self, params):
        self.params = params

    def get_docs(self):
        docs = ["# Disk Analysis",
                "***about disk analysis ***"]
        return '\n'.join(docs)

    def convert_params(self):
        params = [f'dataset=ds']
        for k in ['cx', 'cy', 'r']:
            params.append(f'{k}={self.params[k]}')
        return ', '.join(params)

    def get_plot(self):
        plot = ["plt.figure()",
                "plt.imshow(np.squeeze(disk_result['intensity'].data))"]
        return '\n'.join(plot)


class DiskMaskAnalysis(SingleMaskAnalysis, id_="APPLY_DISK_MASK"):
    TYPE = 'UDF'

    def get_description(self):
        return "intensity of the integration over the selected disk"

    def get_mask_factories(self):
        if self.dataset.shape.sig.dims != 2:
            raise ValueError("can only handle 2D signals currently")
        (detector_y, detector_x) = self.dataset.shape.sig

        cx = self.parameters['cx']
        cy = self.parameters['cy']
        r = self.parameters['r']

        def disk_mask():
            return masks.circular(
                centerX=cx,
                centerY=cy,
                imageSizeX=detector_x,
                imageSizeY=detector_y,
                radius=r,
            )

        return [
            disk_mask,
        ]

    def get_parameters(self, parameters):
        (detector_y, detector_x) = self.dataset.shape.sig

        cx = parameters.get('cx', detector_x / 2)
        cy = parameters.get('cy', detector_y / 2)
        r = parameters.get('r', min(detector_y, detector_x) / 2 * 0.3)
        use_sparse = parameters.get('use_sparse', False)

        return {
            'cx': cx,
            'cy': cy,
            'r': r,
            'use_sparse': use_sparse,
            'mask_count': 1,
            'mask_dtype': np.float32,
        }

    @classmethod
    def get_template_helper(cls):
        return DiskTemplate
