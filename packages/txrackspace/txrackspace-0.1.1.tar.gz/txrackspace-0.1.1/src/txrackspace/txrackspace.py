from twisted.internet import defer, reactor, ssl
from twisted.web import client
from twisted.python import log
import cjson

AUTH_ENDPOINT='https://auth.api.rackspacecloud.com/v1.0'

MAX_RETRIES=2

AUTH_CACHE={}

class RackspaceException(Exception):
  def __str__(self):
    return repr(self.value)

class UnauthorizedException(RackspaceException):
  def __init__(self):
    self.value = 'The X-Auth-Token is not valid or has expired. Re-authenticate to obtain a fresh token.'

class CloudServersFault(RackspaceException):
  def __init__(self, value):
    self.value = value

class RackspaceHTTPPageGetter(client.HTTPPageGetter):

  def handleStatus_204(self):
    pass

  def handleStatus_203(self):
    pass

class RackspaceHTTPClientFactory(client.HTTPClientFactory):
  protocol = RackspaceHTTPPageGetter

  def page(self, page):
    if self.waiting:
      self.waiting = 0
      if not page:
        page = '{}'
      self.deferred.callback({'obj': cjson.decode(page), 'headers': self.response_headers})

class CloudServersAPI(object):

  agent = 'Cloudkick Twisted API'

  def __init__(self, user, key):
    self.user = user
    self.key = key
    self.cache_key = user, key

  ####
  # Servers
  def list_servers(self, details=False):
    return self._run_cmd('servers', details)

  def create_server(self, name, image_id, flavor_id, metadata=None, personality=None):
    data = {'server': {'name': name, 'imageId': image_id, 'flavorId': flavor_id}}
    if metadata: data['server'].update({'metadata': metadata})
    if personality: data['server'].update({'personality': [ personality ]})
    return self._run_cmd('servers', data=data)

  def get_server_details(self, id):
    return self._run_cmd('servers/%s' % (id))

  def update_server_details(self, id, name=None, admin_pass=None):
    data = {'server': {}}
    if not (name or admin_pass):
      raise 'must give at least name or admin_pass'
    if name: data['server'].update({'name': name})
    if admin_pass: data['server'].update({'adminPass': admin_pass})
    return self._run_cmd('servers/%s' % (id), method='PUT', data=data)

  def update_server_name(self, id, name):
    return self.update_server_details(id, name=name)

  def update_server_admin_pass(self, id, admin_pass):
    return self.update_server_details(id, admin_pass=admin_pass)

  def delete_server(self, id):
    return self._run_cmd('servers/%s' % (id), method='DELETE')

  ####
  # Server Addresses
  def list_addresses(self, id):
    return self._run_cmd('servers/%s/ips' % (id))

  def list_public_addresses(self, id):
    return self._run_cmd('servers/%s/ips/public' % (id))

  def list_private_addresses(self, id):
    return self._run_cmd('servers/%s/ips/private' % (id))

  ####
  # Server Actions
  def reboot_server(self, id, type='SOFT'):
    return self._run_cmd('servers/%s/action' % (id), data={'reboot': {'type': type}})

  def rebuild_server(self, id, image_id):
    return self._run_cmd('servers/%s/action' % (id), data={'rebuild': {'imageId': image_id}})

  def resize_server(self, id, flavor_id):
    return self._run_cmd('servers/%s/action' % (id), data={'resize': {'flavorId': flavor_id}})

  def confirm_resized_server(self, id):
    return self._run_cmd('servers/%s/action' % (id), data={'confirmResize': None})

  def revert_resized_server(self, id):
    return self._run_cmd('servers/%s/action' % (id), data={'confirmResize': None})

  def create_image(self, id, name):
    return self._run_cmd('images' % (id), data={'image': {'name': name, 'serverId': id}})

  def share_ip_address(self, id, shared_ip_group, addr):
    return self._run_cmd('servers/%s/actions/share_ip' % (id), data={'shareIp': {'sharedIpGroupId': shared_ip_group, 'addr': addr}})

  def unshare_ip_address(self, id, shared_ip_group, addr):
    return self._run_cmd('servers/%s/actions/unshare_ip' % (id), data={'unshareIp': {'addr': addr}})

  ####
  # Flavors
  def list_flavors(self, details=False):
    return self._run_cmd('flavors', details)

  ####
  # Images
  def list_images(self, details=False):
    return self._run_cmd('images', details)

  ####
  # Backup Schedules
  def list_backup_schedules(self, id):
    return self._run_cmd('servers/%s/backup_schedule' % (id))

  def create_backup_schedule(self, id, enabled, weekly, daily):
    return self._run_cmd('servers/%s/backup_schedule' % (id), data={'backupSchedule': { 'enabled': True, 'weekly': weekly, 'daily': daily}})

  def delete_backup_schedule(self, id):
    return self._run_cmd('servers/%s/backup_schedule' % (id), method='DELETE')

  ####
  # Shared IP Groups
  def list_shared_ip_groups(self, details=False):
    return self._run_cmd('shared_ip_groups', details)

  def create_shared_ip_group(self, name, id):
    data = {'sharedIpGroup': {'name': name, 'server': id}}
    return self._run_cmd('shared_ip_groups', data=data)

  def get_shared_ip_group_details(self, id):
    return self._run_cmd('shared_ip_groups/%s' % (id))

  def delete_shared_ip_group_details(self, id):
    return self._run_cmd('shared_ip_groups/%s' % (id), method='DELETE')

  @defer.inlineCallbacks
  def _run_cmd(self, action, details=False, data=None, method='GET'):
    if details:
      action += '/detail'
    postdata=None
    if data:
      postdata = cjson.encode(data)
      if method != 'PUT': 
        method='POST'

    for i in range(MAX_RETRIES+1):
      try:
        headers, api_endpoint = yield self._get_auth_info()
        url = '%s/%s' % (api_endpoint, action)
        headers.update({'Content-Type': 'application/json', 'Accept': 'application/json'})
        response = yield self._get_page(url, headers=headers, postdata=postdata, method=method)
        defer.returnValue(response['obj'])
      except Exception, e:
        # this does the auth key expiration retries
        if hasattr(e, 'status') and e.status == '401':
          if i < MAX_RETRIES:
            # kill the cache for this object, the next _get_auth_info will fire a request to 
            # the rax auth server
            if AUTH_CACHE.has_key(self.cache_key):
              del AUTH_CACHE[self.cache_key]
          else:
            raise UnauthorizedException()
        elif hasattr(e, 'status') and e.status == '500':
          res = cjson.decode(e.response)
          raise CloudServersFault(res['cloudServersFault']['message'])
        else:
          log.err()
          raise e
    raise 'unable to get response for cmd %s' % (action)

  def _get_page(self, url, **kwargs):
    scheme, host, port, path = client._parse(url)
    factory = RackspaceHTTPClientFactory(url, agent=self.agent, **kwargs)
    contextFactory = ssl.ClientContextFactory()
    reactor.connectSSL(host, port, factory, contextFactory)
    return factory.deferred

  def _get_auth_headers(self):
    return {'X-Auth-User': self.user, 'X-Auth-Key': self.key}

  @defer.inlineCallbacks
  def _get_auth_info(self):
    auth_token, api_endpoint = yield self._get_auth_token()
    defer.returnValue(({'X-Auth-Token': auth_token }, api_endpoint))
    
  @defer.inlineCallbacks
  def _get_auth_token(self):
    headers = self._get_auth_headers()
    if not AUTH_CACHE.has_key(self.cache_key):
      response = yield self._get_page(AUTH_ENDPOINT, headers=headers)
      auth_token = response['headers']['x-auth-token'][0]
      api_endpoint = response['headers']['x-server-management-url'][0]
      AUTH_CACHE[self.cache_key] = auth_token, api_endpoint
    
    defer.returnValue(AUTH_CACHE[self.cache_key])
