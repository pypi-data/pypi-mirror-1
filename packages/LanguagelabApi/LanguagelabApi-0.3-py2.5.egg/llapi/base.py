from exc import ApiError

from urllib2 import urlopen, Request
from urllib import urlencode
from datetime import date, datetime
import simplejson

API_VERSION = 'v1'

class PartnerClient(object):
    def __init__(self, api_key, endpoint='http://testpartner-api.languagelab.com'):
        self.api_key = api_key
        self.endpoint = endpoint
        
        if self.endpoint.endswith("/"):
            self.endpoint = self.endpoint[:-1]
            
        self.base_url = "%s/%s/%s" % (self.endpoint, API_VERSION, self.api_key)
    
    def get_country_code(self, country_name):
        """"This is a convenience method to retrieve the ISO 3166
        country code for a given country name, if it exists."""
        
        response = self._get('register', 'get_country_code', {'name': country_name})
        return response['data']['code']
    
    def get_avatar_lastnames(self):
        """Returns a dictionary of valid last names for the creation of avatars"""
        
        response = self._get('register', 'get_avatar_lastnames')
        return response['data']
    
    def create_user(self, first_name, last_name, dob, email, city, country,
                    avatar_first_name, avatar_last_name_id=None, avatar_last_name=None,
                    existing_avatar=False, password=None):
        """Creates a new user. Returns the user details on successful completion
        and raises ApiError when registration fails."""
        
        # if the country is a string, try converting to a country code
        if isinstance(country, basestring):
            country = self.get_country_code(country)
            
        if isinstance(dob, date):
            dob = str(date)
            
        params = {'first_name': first_name,
                  'last_name': last_name,
                  'dob': dob,
                  'email': email,
                  'city': city,
                  'country_code': country}        
        
        if password:
            params['password'] = password
        
        if existing_avatar:
            params['existing_avatar'] = str(existing_avatar)
            params['avatar_last_name'] = avatar_last_name
        else:
            params['avatar_last_name_id'] = avatar_last_name_id
        
        response = self._post('register', 'create_user', params)
        # TODO: create User objects to return
        return response['data']
    
    def get_user_info(self, user_ids):
        """Returns info for any number of user id's. This will always
        return a list, even if only one user id is passed."""
        if not isinstance(user_ids, list):
            user_ids = [user_ids]
            
        response = self._get('user', 'get_info', {'user_ids': ','.join([str(id) for id in user_ids])})
        return response['data']
    
    def get_user_ids(self):
        """Returns a list of user id's associated with your API key."""
        return self._get('user', 'id_list')['data']
    
    def activate_subscription(self, user_id, sub_type_id):
        """Activates one of the partner's available subscriptions and assigns
        it to the user id passed."""
        params = {'user_id': user_id, 'sub_type_id': sub_type_id}
        return self._post('user', 'activate_subscription', params)['data']
    
    def cancel_subscription(self, user_id):
        """Cancel a user's subscription. The subscription will be active until it
        is due for renewal, at which point it will no longer be renewed."""
        
        return self._post('user', 'cancel_subscription', {'user_id': user_id})['data']
    
    def deactivate_subscription(self, user_id):
        """Deactivates the user's subscription immediately. The user will no
        longer have an active subscription and will not be able to use any services."""
        
        return self._post('user', 'deactivate_subscription', {'user_id': user_id})['data']
        
    def subscription_types(self):
        """Returns a list of available subscription types."""
        # TODO: create a Subscription object
        return self._get('subscription', 'types')['data']
        
    def available_subscriptions(self):
        """Returns the number of available subscriptions on your partner account."""
        return self._get('subscription', 'available_count')['data']
    
    def _post(self, controller, method, params=None):
        if not params:
            params = {}
        return self._api_request(Request(self._url_for(controller, method),
                                        urlencode(params)))
    
    def _get(self, controller, method, params=None):
        url = self._url_for(controller, method)
        if params:
            url = "%s?%s" % (url, urlencode(params))
        return self._api_request(Request(url))
    
    def _url_for(self, controller, method):
        return "%s/%s/%s.json" % (self.base_url, controller, method)
    
    def _api_request(self, request):
        """Sends an API request via the given request object"""
        response = simplejson.loads(urlopen(request).read())
        if not response['status'] == "ok":
            raise ApiError(response['msg'])
        return response
