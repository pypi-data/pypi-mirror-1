import logging

from zope.component import queryMultiAdapter
from Products.CMFCore.utils import getToolByName

logger = logging.getLogger('plonehrm.contracts.events')


def apply_template(object, event, rename=True):
    """After initializing a contract, set text and title based on template.

    If rename is True (the default) we will rename the object after
    setting its title.  Within tests this may fail, so there it can
    help to set it to False.  Yes, this is a hack.
    """
    view = queryMultiAdapter((object, object.REQUEST),
                             name=u'substituter')
    if view is None:
        raise ValueError('Components are not properly configured, could '
                         'not find "substituter" view')

    tool = getToolByName(object, 'portal_contracts', None)
    if tool is None:
        logger.error("portal_contracts cannot be found.")
        return

    # Get the text from the template
    pages = [t for t in tool.listTemplates()
                     if t.getId() == object.template]
    if not pages:
        logger.warn("Template %r cannot be found." % object.template)
        return
    template_page = pages[0]
    template_text = template_page.getText()

    # Save the substituted text on the object.
    resulting_text = view.substitute(template_text)
    object.setText(resulting_text)

    # Set the title to the title of the template (appending 1, 2,
    # 3...), if it has not been set explicitly.
    if object.Title():
        return
    employee = object.get_employee()
    title = template_page.Title()
    if employee is not None:
        numbers = [0]
        for contract in employee.getFolderContents(
            dict(portal_type=object.portal_type)):
            if not contract.Title.startswith(title):
                continue
            number = contract.Title.split(' ')[-1]
            try:
                numbers.append(int(number))
            except ValueError:
                continue
        title += ' %d' % (max(numbers) + 1)
    object.title = title
    # Now we have a title, we rename the object to something nicer
    # than 'contract.2009-05-15.1869364249'.
    if not rename:
        return
    object._renameAfterCreation()
