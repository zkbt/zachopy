'''If something inherits from Talker, then we can print text to the terminal in a relatively standard way.'''
import textwrap

shortcuts = None
line = 100

class Talker(object):
    '''Objects the inherit from Talker have "mute" and "pithy" attributes, a report('uh-oh!') method that prints when unmuted, and a speak('yo!') method that prints only when unmuted and unpithy.'''
    def __init__(self, mute=False, pithy=False, line=line):
        self.mute = mute
        self.pithy = pithy
        self.line = line
        self.nametag = self.__class__.__name__.lower()

    def speak(self, string='', level=0):
        '''If verbose=True and terse=False, this will print to terminal. Otherwise, it won't.'''
        if self.pithy == False:
            self.report(string, level)

    def warning(self, string='', level=0):
        '''If verbose=True and terse=False, this will print to terminal. Otherwise, it won't.'''
        self.report(string, level, prelude=':-| ')


    def input(self, string='', level=0, prompt='(please respond) '):
        '''If verbose=True and terse=False, this will print to terminal. Otherwise, it won't.'''
        self.report(string, level)
        return raw_input("{0}".format(self.prefix + prompt))

    def report(self, string='', level=0, prelude='', abbreviate=True):
        '''If verbose=True, this will print to terminal. Otherwise, it won't.'''
        if self.mute == False:
            self.prefix = prelude + '{spacing}[{name}] '.format(name = self.nametag, spacing = ' '*level)
            self.prefix = "{0:>16}".format(self.prefix)
            equalspaces = ' '*len(self.prefix)
            toprint = string + ''
            if abbreviate:
                if shortcuts is not None:
                    for k in shortcuts.keys():
                        toprint = toprint.replace(k, shortcuts[k])

            print textwrap.fill(self.prefix + toprint.replace('\n', '\n' + equalspaces), self.line, subsequent_indent=equalspaces + '... ')
