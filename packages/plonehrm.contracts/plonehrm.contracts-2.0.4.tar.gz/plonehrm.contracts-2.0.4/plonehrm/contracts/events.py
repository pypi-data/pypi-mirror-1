from zope.component import queryMultiAdapter
from Products.CMFCore.utils import getToolByName


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
    if tool is None or object.template not in tool.contentIds():
        # Hm, odd.
        return

    # Get the text from the template
    template_page = tool[object.template]
    template_text = template_page.getText()

    # Save the substituted text on the object.
    resulting_text = view.substitute(template_text)
    object.setText(resulting_text)

    # Set the title.
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
