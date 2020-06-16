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

message_template_html = """
<html>
    <body>
        <p>
            Thank you for the note! Here is what you sent to Ryan:
        </p>
        <ul>
            <li>First Name: ${fname}</li>
            <li>Last Name: ${lname}</li>
            <li>Email Address: ${email}</li>
            <li>Message: ${msg}</li>
            <li>Time Stamp: ${time}</li>
        </ul>
        <p>
            Thanks again! <br>
            Email: rsfogle2@illinois.edu <br>
            Cell: (309) 310-7926 <br>
            Website: ryan-fogle.com <br>
        </p>
    </body>
</html>

"""
message_template_html = Template(message_template_html)
message_template = Template(message_template)
