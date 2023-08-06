CMFQuestionnaire is a simple questionnaire add-on for Plone.
Its main features are:

  * user-based or anonymous submissions (through a ticket system)

  * pdf report creation with bar and pie charts for each question
    (requires `reportlab`_)

  * internationalization

  * creates only 1 portal type for the questionnaire which is
    internally represented as an XML document

.. _reportlab: http://www.reportlab.org/

Using

  * add a questionnaire like any other content type

    check 'use_ticket' if you want to use tickets (see below)

  * go to 'design' tab

  * add a question or a group:

    * enter the title of the group

    * enter the scale of the group (the options will be numbered from
      1 to this value)

    * enter the legend to explain the options (put one option on each
      line, starting with the option for 1)

    * optionally, enter a description for the group

    * add / remove questions to the group

  * repeat for other groups if you have more

  * publish the questionnaire (questionnaires can only be filled out
    between their start and expiry dates)

  * go to the Zope Management Interface, the 'Security' tab and check
    the permissions on who can add, edit, fill-out and view the results
    of the questionnaire

  * go to the 'evaluate' tab and see the results or get a PDF report

  Tickets

    This mechanism was implemented to fulfil a need of my department
    here at the Istanbul Technical University. At the end of each
    term we present students with questionnaires for each course
    they have taken in that term. Since our students have no users
    on our site, we decided to hand out tickets that would enable
    them to fillout the questionnaires even as anonymous visitors.
    If you have a similar case, here's how it works:

    * when editing the questionnaire, check 'use_ticket'

    * go to the 'tickets' tab and create as many tickets as you like
      (multiples of 15 are recommended, since they can be printed out
      on a page)

    * select 'list available tickets' and print that page
      (*note*: the number of tickets displayed are always a multiple
      of 3, so you may not be able to see the last 1 or 2 tickets)

    * hand out the tickets to people you would like to participate
      in the questionnaire

You can always find the latest information about CMFQuestionnaire on its
`web page`_.  The source code is kept in a Subversion `repository`_.

.. _web page: http://plone.org/products/cmfquestionnaire
.. _repository: http://svn.plone.org/svn/collective/CMFQuestionnaire/
