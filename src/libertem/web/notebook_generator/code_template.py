from libertem.analysis.base import Analysis
from .template import TemplateBase


class CodeTemplate(TemplateBase):
    """
    Generate code using template from :class:`TemplateBase` and parameters
    from GUI.

    new code segments can be generated by adding templates in :class:`TemplateBase`
    and combining parameters accordingly.

    code for dataset, dependencies, connection are generated here. Analysis
    specific code are handled in `libertem.analysis.helper`.
    """

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
        return self.code_formatter(self.format_template(self.temp_ds, data))

    def dependency(self):
        """
        dependencies required for generated script.

        Common dependencies are available in :class:`TemplateBase`.
        Any additional dependencies can be added through
        corresponding analysis helper.
        """
        extra_dep = []
        for helper in self.analysis_helper.values():
            analysis_dep = helper.get_dependency()
            if analysis_dep is not None:
                extra_dep.extend(analysis_dep)
        dep = self.temp_dep + extra_dep
        return self.code_formatter('\n'.join(dep))

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

            plot_ = list(map(self.code_formatter, helper.get_plot()))
            analy_ = self.code_formatter(helper.get_analysis())
            docs_ = self.code_formatter(helper.get_docs())
            save_ = self.code_formatter(helper.get_save())

            form_analysis.append((docs_, analy_, plot_, save_))

        return form_analysis
