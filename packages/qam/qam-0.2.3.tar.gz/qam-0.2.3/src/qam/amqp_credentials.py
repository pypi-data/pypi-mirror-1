

class AMQPCredentials:
  def __init__(self,
               hostname="localhost",
               port=5672,
               username='guest',
               password='guest',
               vhost='/',
               ssl=False):
    self.hostname = hostname
    self.port = port
    self.username = username
    self.password = password
    self.vhost = vhost
    self.ssl = ssl