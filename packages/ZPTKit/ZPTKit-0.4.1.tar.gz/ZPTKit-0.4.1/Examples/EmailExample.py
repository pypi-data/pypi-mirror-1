from ZPTExample import ZPTExample

class EmailExample(ZPTExample):

    def awake(self, trans):
        ZPTExample.awake(self, trans)
        req = self.request()
        self.options.formAction = self.__class__.__name__
        if not self.toAddresses() or not self.smtpServer():
            # They have to configure the email sending first
            self.setView('EmailExample_error.pt')

    def actions(self):
        return ['send']

    def toAddresses(self):
        app = self.request().transaction().application()
        headers = app.setting('ErrorEmailHeaders', None)
        if headers is None or headers['To'] == ['-@-.com']:
            return None
        return headers['To']

    def smtpServer(self):
        app = self.request().transaction().application()
        host = app.setting('ErrorEmailServer', None)
        if host is None or host == 'mail.-.com':
            return None
        return host
            
    def send(self):
        req = self.request()
        from_address = req.field('from')
        to_addresses = self.toAddresses()
        subject = req.field('subject')
        body = req.field('body')
        self.sendMail('EmailExample_email.pt',
                      to_addresses,
                      from_address,
                      subject=subject,
                      body=body,
                      smtp_server=self.smtpServer())
        print "Email sent"
        self.write('Email sent!')
        self.setView(None)
