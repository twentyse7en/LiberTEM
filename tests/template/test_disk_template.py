import io
import os
import numpy as np
import nbformat
from temp_utils import _get_hdf5_params
from libertem.web.notebook_generator.notebook_generator import notebook_generator
from nbconvert.preprocessors import ExecutePreprocessor


def test_disk_default(hdf5_ds_2, tmpdir_factory, lt_ctx):
    datadir = tmpdir_factory.mktemp('template_tests')

    conn = {'connection': {'type': 'local'}}
    path = hdf5_ds_2.path
    dataset = _get_hdf5_params(path)

    analysis = [{
            "analysisType": 'APPLY_DISK_MASK',
            "parameters": {
                    'shape': 'disk',
                    'cx': 8,
                    'cy': 8,
                    'r': 5,
                    }
    }]

    notebook = notebook_generator(conn, dataset, analysis, save=True)
    notebook = io.StringIO(notebook.getvalue())
    nb = nbformat.read(notebook, as_version=4)
    ep = ExecutePreprocessor(timeout=600)
    out = ep.preprocess(nb, {"metadata": {"path": datadir}})
    data_path = os.path.join(datadir, 'disk_result.npy')
    results = np.load(data_path)

    disk_analysis = lt_ctx.create_disk_analysis(
                                        dataset=hdf5_ds_2,
                                        cx=8,
                                        cy=8,
                                        r=5)
    expected = lt_ctx.run(disk_analysis)

    assert np.allclose(
        results,
        expected['intensity'].raw_data,
    )
