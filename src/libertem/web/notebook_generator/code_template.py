from libertem.analysis.base import Analysis
from .template import TemplateBase


class CodeTemplate(TemplateBase):

    def __init__(self, connection, dataset, compound_analysis):
        self.conn = connection['connection']
        self.ds = dataset
        self.compound_analysis = compound_analysis

        self.analysis_helper = {}
        for analysis in self.compound_analysis:

            type = analysis['analysisType']
            params = analysis['parameters']
            cls = Analysis.get_analysis_by_type(type)
            helperCls = cls.get_template_helper()
            helper = helperCls(params)
            self.analysis_helper[type] = helper

    def dataset(self):
        ds_type = self.ds['type']
        ds_params = self.ds['params']
        data = {'type': ds_type, 'params': ds_params}
        return self.format_template(self.temp_ds, data)

    def dependency(self):

        for helper in self.analysis_helper.values():
            extra_dep = helper.get_dependency()
            if extra_dep is not None:
                self.temp_dep.extend(extra_dep)

        return '\n'.join(self.temp_dep)

    def initial_setup(self):
        return "%matplotlib nbagg"

    def connection(self):
        docs = ["# Connection"]
        if (self.conn['type'] == "cluster"):
            link = "https://libertem.github.io/LiberTEM/usage.html#starting-a-custom-cluster"
            more_info = f"[For more info]({link})"
            docs.append(f"Connecting to dask cluster, {more_info}")
            data = {'conn_url': self.conn['url']}
            ctx = self.format_template(self.temp_conn, data)
            docs = '\n'.join(docs)
            return ctx, docs
        else:
            docs.append("This starts a local cluster that is accessible through ctx.")
            ctx = "ctx = lt.Context()"
            docs = '\n'.join(docs)
            return ctx, docs

    def analysis(self):

        form_analysis = []

        for helper in self.analysis_helper.values():

            plot_ = helper.get_plot()
            analy_ = helper.get_analysis()
            docs_ = helper.get_docs()

            form_analysis.append((docs_, analy_, plot_))

        return form_analysis
