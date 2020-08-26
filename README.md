# GoogleAds Remarketing Email Upload

By default this script connects to Oracle database, creates a pandas dataframe and creates a list of emails.

This process can be changed by providing any list of emails within get_customer_email() and then apply the following function for encoding before passing it on:
```emails = [x.encode('utf-8') for x in emails]```

FZ
