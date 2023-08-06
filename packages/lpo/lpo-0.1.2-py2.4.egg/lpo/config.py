import logging

logging.basicConfig(level=logging.DEBUG,
                    format='\n\n%(message)s',
                    filename='/tmp/expr.log',
                    filemode='w')


URL = 'postgres://postgres@localhost:5432/test'
#URL = 'sqlite://'
