'''If something inherits from Talker, then we can print text to the terminal in a relatively standard way.'''
import textwrap, numpy as np, pprint

shortcuts = None
line = np.inf

class Talker(object):
    '''Objects the inherit from Talker have "mute" and "pithy" attributes, a report('uh-oh!') method that prints when unmuted, and a speak('yo!') method that prints only when unmuted and unpithy.'''
    def __init__(self, nametag=None, mute=False, pithy=False, line=line):
        self._mute = mute
        self._pithy = pithy
        self._line = line
        if nametag is None:
            self.nametag = self.__class__.__name__.lower()
        else:
            self.nametag = nametag

    def speak(self, string='', level=0, progress=False):
        '''If verbose=True and terse=False, this will print to terminal. Otherwise, it won't.'''
        if self._pithy == False:
            self.report(string=string, level=level, progress=progress)

    def warning(self, string='', level=0):
        '''If verbose=True and terse=False, this will print to terminal. Otherwise, it won't.'''
        self.report(string, level, prelude=':-| ')

    def input(self, string='', level=0, prompt='(please respond) '):
        '''If verbose=True and terse=False, this will print to terminal. Otherwise, it won't.'''
        self.report(string, level)
        return input("{0}".format(self._prefix + prompt))

    def report(self, string='', level=0, prelude='', progress=False, abbreviate=True):
        '''If verbose=True, this will print to terminal. Otherwise, it won't.'''
        if self._mute == False:
            self._prefix = prelude + '{spacing}[{name}] '.format(name = self.nametag, spacing = ' '*level)
            self._prefix = "{0:>16}".format(self._prefix)
            equalspaces = ' '*len(self._prefix)
            toprint = string + ''
            if abbreviate:
                if shortcuts is not None:
                    for k in shortcuts.keys():
                        toprint = toprint.replace(k, shortcuts[k])

            if progress:
                print('\r' + self._prefix + toprint.replace('\n', '\n' + equalspaces),)
            else:
                print(self._prefix + toprint.replace('\n', '\n' + equalspaces))

            #print textwrap.fill(self._prefix + toprint.replace('\n', '\n' + equalspaces), self._line, subsequent_indent=equalspaces + '... ')

    def summarize(self):
        '''Print a summary of the contents of this object.'''

    def summarize(self):
        self.speak('Here is a brief summary of {}.'.format(self.nametag))
        s = '\n'+pprint.pformat(self.__dict__)
        print(s.replace('\n', '\n'+' '*(len(self._prefix)+1)) + '\n')
