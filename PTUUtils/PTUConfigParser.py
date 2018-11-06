import configparser
class PTUConfigParser(configparser.ConfigParser):
    def __init__(self,defaults=None):
        configparser.ConfigParser.__init__(self,defaults=None)
    def optionxform(self, optionstr):
        return optionstr


if __name__ == '__main__':
    conf = PTUConfigParser()
    conf.add_section('Section1')
    conf.set('Section1', 'AAN_int', '15')
    conf.set('Section1', 'a_bKKool', 'true')

    # Writing our configuration file to 'example.cfg'
    with open('example.cfg', 'w') as configfile:
        conf.write(configfile)
