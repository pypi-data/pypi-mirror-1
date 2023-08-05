To use Turbo-Mail you need to perform the following actions:

1. Add the following to the general section of your dev.cfg, prod.cfg or app.cfg: (the defaults are shown)

	mail.on = True # Boolean; This must be enabled for any processing to take place.
	mail.server = None # String; Required.
	mail.username = None # String; If both username and password are not None authentication will be used.
	mail.password = None # String
	mail.sender = None # String; Used by the sample below to centralize sender e-mail address.
	mail.debug = False # Boolean; Enabling this will output all communications between SMTP server and client.
	mail.interval = 10 # Integer; Interval between queue checks in seconds.
	mail.threads = 4 # Integer; Maximum number of concurrent threads.
	mail.jobs = 10 # Integer; Maximum number of work units per thread.
	mail.timeout = 60 # Integer; Time a thread will remain alive waiting for new work units in seconds.

2. At the location you wish to send e-mail:

	0. Import TurboMail.

		e.g.:
			import turbomail

	1. Create an instance of a Message object.  Two are included: Message and TemplateMessage.
	
		e.g.:
			id = user.id
			message = turbomail.TemplateMessage(
					turbogears.config.get("mail.sender", None),
					user.email,
					_("Welcome to the booking system."),
					"myapp.templates.mail.welcome",
					dict(employee=lambda: model.Employee.get(id))
				)
	
	2. Enqueue the message.
	
		e.g.:
			turbomail.enqueue(message)

   Note that you can pass a callable as the value of arguments passed to KID by TemplateMessage.  These will be executed during initial message compilation - usually just before the message is sent.  This is important if you wish to pass SQLObject-based data to an e-mail template.  The example above gets around thread-based limitations by retrieving the record just before the template is evaluated.

Lots of debugging information will be output - modify your logging rules to filter out the noise.  All loggers are prefixed with 'turbomail', with SMTP connection information using 'turbomail.dispatch', queue and thread pool management 'turbomail.pool'.

Enjoy!