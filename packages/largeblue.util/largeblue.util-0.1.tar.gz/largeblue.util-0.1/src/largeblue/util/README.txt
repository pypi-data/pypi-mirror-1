Atm largeblue.util just has an emailer utitity for sending emails, which wraps the 
zope.sendmail functionality, plus a batch utility which can be used to batch search results 
/ listings etc.::

    >>> from largeblue.util.interfaces import IEmail, IBatch
    >>> from zope.component import getUtility

The package configures the two utilities so they're lookable-upable (after all zcml 
registrations have been parsed) under::

    >>> getUtility(IEmail)
    <class 'largeblue.util.emailer.Email'>

    >>> getUtility(IBatch)
    <class 'largeblue.util.batch.Batch'>

You'll need to configure your own smtpMailer & queuedDelivery utilities (these should be 
done manually for each site / instance - see the comment in configure.zcml).