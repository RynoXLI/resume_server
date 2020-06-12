from string import Template

message_template = "Hello ${fname},\n\n" \
                               "Thank you for the note! Here is what you sent to Ryan:\n" \
                               "First Name: ${fname}\n" \
                               "Last Name: ${lname}\n" \
                               "Email Address: ${email}\n" \
                               "Message: ${msg}\n" \
                               "Time Stamp: ${time}\n\n" \
                               "Thanks again!\n" \
                               "Ryan Fogle\n" \
                               "Email: rsfogle2@illinois.edu\n" \
                               "Cell: (309) 310-7926\n" \
                               "Website: ryan-fogle.com"

message_template = Template(message_template)
