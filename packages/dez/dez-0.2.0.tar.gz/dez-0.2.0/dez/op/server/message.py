class OPMessage(object):
    def __init__(self, payload, recipients, complete_cb, cb_arg=[]):
        self.payload = payload
        self.recipients = recipients
        self.complete_cb = complete_cb
        self.cb_arg = cb_arg
        self.failed = []
        self.succeeded = []

    def single_recipient_event(self, recipient):
        return SingleRecipientMessage(
            self.payload, recipient, self.success, self.failure)

    def success(self, recipient):
        self.succeeded.append(recipient)
        self.check_complete()

    def failure(self, recipient, reason):
        self.failed.append((recipient, reason))
        self.check_complete()

    def check_complete(self):
        if len(self.failed) + len(self.succeeded) == len(self.recipients):
            self.complete_cb(self.succeeded, self.failed, *self.cb_arg)

class SingleRecipientMessage(object):
    def __init__(self, payload, recipient, success_cb, failure_cb):
        self.payload = payload
        self.recipient = recipient
        self.success_cb = success_cb
        self.failure_cb = failure_cb

    def success(self):
        self.success_cb(self.recipient)

    def failure(self, reason="unknown"):
        self.failure_cb(self.recipient, reason)