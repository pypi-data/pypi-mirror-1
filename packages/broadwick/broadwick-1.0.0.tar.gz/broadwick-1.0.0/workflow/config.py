 
class sql:
    url = 'mysql://root:daisya@localhost/intent'
    echo=False
    create = True
    drop = False
    
    
class web:
    port = 8080
    

class xml:
    port = 8081
    title = 'Process Server'
    description = "I start business processes"
    

class stomp:
    host = 'localhost'
    port = 61613
    login = 'process_stomp_pc'
    reconnect = True


class dojo:
    path = '/Users/peterb/Workshop/Javascript/dojo-release-1.2.0/'
