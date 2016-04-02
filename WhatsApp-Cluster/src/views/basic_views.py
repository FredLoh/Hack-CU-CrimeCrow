from yowsup.layers.protocol_messages.protocolentities import TextMessageProtocolEntity
import random


def echo(message, match):
    return TextMessageProtocolEntity("Echo: %s" % match.group("echo_message"), to=message.getFrom())


def ping(message, match):
    words = ['hello', 'apple', 'something', 'yeah', 'nope', 'lalala']
    random_string = ' '.join(random.choice(words) for _ in range(5))
    return TextMessageProtocolEntity(("Still alive." + random_string), to=message.getFrom())
