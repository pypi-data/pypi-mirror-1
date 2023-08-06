Dear ${c.firstname or c.username},
% if c.email_type == 'register':

Thank you for registering. Your verification code is ${ c.verify }.

In order to complete your registration please visit the following URL:
% elif c.email_type == 'reminder':
You requested a reminder of your verification code for this email address, it is ${ c.verify }.

Please visit the following URL to confirm this email address:
% endif

${c.confirm_url}

Enjoy the site!

Best wishes,

The Team
