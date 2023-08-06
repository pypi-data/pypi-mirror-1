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

    def opt_out_recipient(api_url, list_id, email):
        """opt out a recipient from a list
           api_url, list_id, email are required
           returns True or False
        """

    def xml_request(api_url, xml):
        """submit a custom xml request
           api_url, xml, are required
           returns a string (xml)
        """

- Silverpop: http://www.silverpop.com/
