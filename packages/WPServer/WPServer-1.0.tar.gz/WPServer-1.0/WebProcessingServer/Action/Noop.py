from WebProcessingServer.Action import Action

class Noop(Action):
   def action(self, request):
        return request
