from allauth.account.adapter import DefaultAccountAdapter


class AccountAdapter(DefaultAccountAdapter):
    """Custom Account Adapter

    Whenever a user confirms their email, check
    if the email being confirmed is the academic
    email and, if the user signed up using a social
    account that provided an email, set that as the
    primary email instead of the academic one
    """

    def confirm_email(self, request, email_address):
        email_address.verified = True
        email_address.set_as_primary(conditional=True)
        email_address.save()
        # Checks if the email being confirmed is the university email
        if getattr(email_address.user, 'student', None) is not None and email_address.email == email_address.user.student.university_email:
            # Check if there are any other emails available (i.e. social emails)
            other_emails = email_address.user.emailaddress_set.exclude(pk=email_address)
            if other_emails.exists():
                # get the first, verify it and set as primary
                other_email = other_emails.first()
                other_email.verified = True
                other_email.set_as_primary()
                other_email.save()
