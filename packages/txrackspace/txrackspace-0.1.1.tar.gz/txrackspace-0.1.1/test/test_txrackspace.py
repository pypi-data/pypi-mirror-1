from twisted.trial import unittest
from twisted.internet import defer
from twisted.web.error import Error

from txrackspace import CloudServersAPI

from secrets import USERNAME, API_KEY

# ugly hack because testing web services sucks

class TestCloudServers(unittest.TestCase):

  SERVER = None

  @defer.inlineCallbacks
  def setUp(self):
    self.api = CloudServersAPI(USERNAME, API_KEY)
    if not self.SERVER:
      res = yield self.api.list_servers()
      for server in res['servers']:
        if server['name'] == 'txrackspace-unittest-001':
          self.SERVER = server
      

  @defer.inlineCallbacks
  def test_list_servers(self):
    res = yield self.api.list_servers()
    self.assertTrue(res)

#  @defer.inlineCallbacks
#  def disabled_test_001_create_server(self):
#    self.server_name = 'txrackspace-unittest-001'
#    res = yield self.api.create_server(name=self.server_name, image_id=8, flavor_id=1)

  @defer.inlineCallbacks
  def test_get_server_details(self):
    res = yield self.api.get_server_details(self.SERVER['id'])
    self.assertEqual(res['server']['name'], self.SERVER['name'])

  # TODO: update_server_name
  # TODO: update_server_admin_pass

#  @defer.inlineCallbacks
#  def disabled_test_delete_server(self):
#    res = yield self.api.delete_server(self.SERVER['id'])

  @defer.inlineCallbacks
  def test_list_addresses(self):
    res = yield self.api.list_addresses(self.SERVER['id'])
    self.assertTrue(res)

  @defer.inlineCallbacks
  def test_list_public_addresses(self):
    res = yield self.api.list_public_addresses(self.SERVER['id'])
    self.assertTrue(res)

  @defer.inlineCallbacks
  def test_list_public_addresses(self):
    res = yield self.api.list_private_addresses(self.SERVER['id'])
    self.assertTrue(res)

  @defer.inlineCallbacks
  def test_list_flavors(self):
    res = yield self.api.list_flavors(details=True)
    self.assertTrue(len(res['flavors']) > 2)

  @defer.inlineCallbacks
  def test_list_images(self):
    res = yield self.api.list_images()
    self.assertTrue(len(res['images']) > 2)


  ###
  # Backup Schdules
  @defer.inlineCallbacks
  def test_backup_schedules(self):
    yield self.api.create_backup_schedule(self.SERVER['id'], enabled=True, weekly='THURSDAY', daily='H_0400_0600')

    res = yield self.api.list_backup_schedules(self.SERVER['id'])
    self.assertEqual(res['backupSchedule']['weekly'], 'THURSDAY')

    yield self.api.delete_backup_schedule(self.SERVER['id'])

    res = yield self.api.list_backup_schedules(self.SERVER['id'])
    self.assertEqual(res['backupSchedule']['enabled'], False)

  ###
  # Shared IP groups
  @defer.inlineCallbacks
  def test_shared_ip_group(self):
    shared_ip_group = 'txrackspace-unittest-shared-ip-group-001'
    res = yield self.api.create_shared_ip_group(name=shared_ip_group, id=self.SERVER['id'])
    id = res['sharedIpGroup']['id']
    self.assertEqual(res['sharedIpGroup']['name'], shared_ip_group)

    res = yield self.api.list_shared_ip_groups()
    self.assertEqual(res['sharedIpGroups'][0]['name'], shared_ip_group)

    res = yield self.api.get_shared_ip_group_details(id)
    self.assertEqual(res['sharedIpGroup']['name'], shared_ip_group)
    self.assertEqual(res['sharedIpGroup']['id'], id)

    res = yield self.api.delete_shared_ip_group_details(id)

