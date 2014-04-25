After updating your main.cf and your Dovecot configuration you can now add alias domains to ViMbAdmin:

1. Create new domain _example.net_ which we want to alias to _example.com_
2. Create new alias on _example.net_ named _*@example.net_ that forwards to _*@example.com_
3. Test send an email to _user@example.com_ and _user@example.net_ and verify both messages are delivered successfully to _user@example.com_

Users can log in to Dovecot (IMAP/POP3/SMTP AUTH) using either _example.net_ or _example.com_. If login fails to find the username/password combo on the first try, it will attempt to look it up in the alias table, and allow login if that succeeds. This way users can configure their mail clients however they please.

