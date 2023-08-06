
import execnet
gw = execnet.PopenGateway("python3")
channel = gw.remote_exec("channel.send('somestring')")
string_from_remote = channel.receive()
print (repr(string_from_remote))
