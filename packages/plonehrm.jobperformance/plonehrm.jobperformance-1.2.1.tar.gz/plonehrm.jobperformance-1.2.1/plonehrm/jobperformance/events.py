from Products.plonehrm.utils import apply_template_of_tool


def apply_template(object, event):
    """After initializing a job performance interview, set text based
    on template.
    """
    apply_template_of_tool(object, 'portal_jobperformance')
