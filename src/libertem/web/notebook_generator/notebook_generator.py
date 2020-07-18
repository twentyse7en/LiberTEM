import io
import nbformat as nbf
from .code_template import CodeTemplate


class Notebook:
    '''
    Interface for creating jupyter notebook.
    '''
    def __init__(self):
        self.nb = nbf.v4.new_notebook()

    def add_code(self, code_):
        new_cell = nbf.v4.new_code_cell(code_)
        self.nb['cells'].append(new_cell)

    def add_doc(self, doc_):
        new_cell = nbf.v4.new_markdown_cell(doc_)
        self.nb['cells'].append(new_cell)

    def generate(self):
        f = io.StringIO()
        nbf.write(self.nb, f)
        return f


def notebook_generator(conn, dataset, comp, save=False):
    '''
    Generates a jupyter notebook file using the code
    generated by :class:`CodeTemplate`.

    For creating additional code/doc cell, generate
    code in :class:`CodeTemplate` and add cell here.
    '''
    # initialization
    nb = Notebook()
    instance = CodeTemplate(conn, dataset, comp)

    nb.add_code(instance.dependency())
    nb.add_code(instance.initial_setup())

    ctx, conn_docs = instance.connection()
    nb.add_doc(conn_docs)
    nb.add_code(ctx)
    nb.add_code(instance.dataset())

    for docs, analysis, plots, store in instance.analysis():
        nb.add_doc(docs)
        nb.add_code(analysis)
        for plot in plots:
            nb.add_code(plot)
        if save:
            nb.add_code(store)

    return nb.generate()
