"""Configuration module for pysvnbot."""

# Where should the IPC socket reside?
ipc_socket = "/tmp/pysvnbot-ipc.sock"

# Which servers and channels should get the messages?
# key = remote address, value = passed to the IRC class' constructor by **d.
# The autojoin key can be a sequence or a dict-like object, if the latter, the
# key is taken as the channel name and the value is the password. You can not
# mix these, and I'm working on a solution to that problem.
ircs = {
    ("irc.lericson.se", 6668): {"nickname": "pysvnbot-test",
        "username": "pysvnbot", "realname": "HAL9000", "autojoin": ("#test",)},
    ("irc.oftc.net", 6667): {"nickname": "pysvnbot-test",
        "username": "pysvnbot", "realname": "HAL9000",
        "autojoin": ("#toxik.fanclub",)}
}
