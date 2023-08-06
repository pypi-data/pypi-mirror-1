silverpop
=========

Python implementation of the Silverpop API

Currently implemented API methods::

    def add_recipient(api_url, list_id, email, columns=[]):
        """Add recipient to a list (only email key supported)
           api_url, list_id, email are required, optionally
           takes a list of dicts to define additional columns like
           [{'column_name':'State', 'column_value':'Germany'},]
           returns True or False
        """

    def update_recipient(api_url, list_id, old_email, columns=[]):
        """Update recipient of a list,
           if the old_email is not a recipient of the list, a recipient will be added.
           api_url, list_id, old_email are required, optionally
           takes a list of dicts to define additional columns like:
           [{'column_name':'State', 'column_value':'Germany'},]
           Can change the email of a recipient by specifiying a column like:
           {'column_name':'EMAIL', 'column_value':'new@email.com'}
           Can re-opt-in an opted-out recipient by specifying a column like:
           {'column_name':'OPT_OUT', 'column_value':'False'}
           returns True or False
        """

    def opt_in_recipient(api_url, list_id, email, columns=[]):
        """opt in a recipient to a list (only email key supported)
           api_url, list_id, email are required, optionally
           takes a list of dicts to define additional columns like
           [{'column_name':'State', 'column_value':'Germany'},]
           returns True or False
        """

    def is_opted_in(api_url, list_id, email):
        """Is the specified email opted in to the list?
           api_url, list_id, email are required
           returns True or False
        """

    def opt_out_recipient(api_url, list_id, email):
        """opt out a recipient from a list
           api_url, list_id, email are required
           returns True or False
        """

    def select_recipient_data(api_url, list_id, email, column=None):
        """get the recipients data
           api_url, list_id, email are required
           you may specify a column dict for non email key lists, like
           {'column_name': 'USER_ID', 'column_value': '4711'}
           returns the silverpop response (xml)
        """

    def xml_request(api_url, xml):
        """submit a custom xml request
           api_url, xml, are required
           returns the silverpop response (xml)
        """

- Silverpop: http://www.silverpop.com/
