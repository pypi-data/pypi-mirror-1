
from kss.core import KSSView, kssaction

class ParameterFunctionView(KSSView):

    @kssaction
    def submitFullForm(self, form):
        assert hasattr(form, 'keys'), 'Form data is expected to be a dict-like object.'
        # marshall back the repr of this dict.
        ksscore = self.getCommandSet('core')
        ksscore.replaceInnerHTML('#target', repr(form))

    @kssaction
    def submitFullFormIntoRequest(self):
        # marshall back the repr of this dict.
        ksscore = self.getCommandSet('core')
        ksscore.replaceInnerHTML('#target', repr(self.request.form))
