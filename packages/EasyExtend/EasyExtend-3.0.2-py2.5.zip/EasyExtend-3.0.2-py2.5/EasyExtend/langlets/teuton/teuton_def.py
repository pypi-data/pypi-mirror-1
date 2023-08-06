class teuton_bool(int):
    def __init__(self,i):
        int.__init__(self,i)

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

Wahr = teuton_bool(True)
Wahr.name = "Wahr"

Falsch = teuton_bool(False)
Falsch.name = "Falsch"

class NichtsTyp(object):
    def __eq__(self, other):
        return other in (Nichts, None)

    def __neq__(self, other):
        return other not in (Nichts, None)

    def __nonzero__(self):
        return False

    def __repr__(self):
        return "Nichts"

    def __str__(self):
        return "Nichts"

Nichts = NichtsTyp()

teuton_std_lib = {
    'ArithmetischerFehler' : 'ArithmeticError',
    'AnnahmeFehler' : 'AssertionError',
    'AttributFehler' : 'AttributeError',
    'VeraltetWarnung' : 'DeprecationWarning',
    'EndeDerDateiFehler' : 'EOFError',
    'Ellipse' : 'Ellipsis',
    'UmgebungsFehler' : 'EnvironmentError',
    'Ausnahme' : 'Exception',
    'FliesskommaFehler' : 'FloatingPointError',
    'ZukunftsWarnung' : 'FutureWarning',
    'EAFehler' : 'IOError',
    'ImportFehler' : 'ImportError',
    'EinrueckungsFehler' : 'IndentationError',
    'IndexFehler' : 'IndexError',
    'SchluesselFehler' : 'KeyError',
    'TastaturUnterbrechung' : 'KeyboardInterrupt',
    'NachsehenFehler' : 'LookupError',
    'SpeicherFehler' : 'MemoryError',
    'NamensFehler' : 'NameError',
    'Nichts' : 'None',
    'NichtImplementiert' : 'NotImplemented',
    'NichtImplementiertFehler' : 'NotImplementedError',
    'BetriebssystemFehler' : 'OSError',
    'UeberGrenzeHinausFehler' : 'OverflowError',
    'PendingDeprecationWarnung' : 'PendingDeprecationWarning',
    'ReferenzFehler' : 'ReferenceError',
    'LaufzeitFehler' : 'RuntimeError',
    'LaufzeitWarnung' : 'RuntimeWarning',
    'StandardFehler' : 'StandardError',
    'StopIteration' : 'StopIteration',
    'SyntaxFehler' : 'SyntaxError',
    'SyntaxWarnung' : 'SyntaxWarning',
    'SystemFehler' : 'SystemError',
    'SystemAusgang' : 'SystemExit',
    'TabFehler' : 'TabError',
    'TypFehler' : 'TypeError',
    'UngebundenLokalFehler' : 'UnboundLocalError',
    'UnicodeDekodierungsFehler' : 'UnicodeDecodeError',
    'UnicodeCodierungsFehler' : 'UnicodeEncodeError',
    'UnicodeFehler' : 'UnicodeError',
    'UnicodeUerbersetzungsFehler' : 'UnicodeTranslateError',
    'BenutzerWarnung' : 'UserWarning',
    'WertFehler' : 'ValueError',
    'Warnung' : 'Warning',
    'FensterFehler' : 'WindowsError',
    'NullDivisionsFehler' : 'ZeroDivisionError',
    'verwende' : 'apply',
    'basisstring' : 'basestring',
    'puffer' : 'buffer',
    'aufrufbar' : 'callable',
    'klassenmethode' : 'classmethod',
    'vgl' : 'cmp',
    #'coerce' : 'coerce',        # ???
    'kompiliere' : 'compile',
    'komplex' : 'complex',
    'copyright' : 'copyright',
    'wuerdigung' : 'credits',
    'entfattr' : 'delattr',
    'lexikon' : 'dict',
    'verz' : 'dir',
    'aufzaehlung' : 'enumerate',
    #'execfile' : 'execfile',  #  ???
    'raus' : 'exit',
    'datei' : 'file',
    'filter' : 'filter',
    'fliesskomma' : 'float',
    #'frozenset' : 'frozenset', # ???
    'nimmattr' : 'getattr',
    'globals' : 'globals',
    'hatattr' : 'hasattr',
    'hilfe' : 'help',
    'eingabe' : 'input',
    'ganzzahl' : 'int',
    'istinstanz' : 'isinstance',
    'istunterklasse' : 'issubclass',
    'iter' : 'iter',
    'laenge' : 'len',
    'lizenz' : 'license',
    'liste' : 'list',
    'lokal' : 'locals',
    'langzahl' : 'long',
    'bilde_ab' : 'map',
    'objekt' : 'object',
    'oeffne' : 'open',
    'ord' : 'ord',
    'hoch' : 'pow',
    'eigenschaft' : 'property',
    'schliesse' : 'quit',
    'intervall' : 'range',
    'roh_eingabe' : 'raw_input',
    'bereich':'range',
    'reduziere' : 'reduce',
    'lade_neu' : 'reload',
    'umgekehrt' : 'reversed',
    'runde' : 'round',
    'menge' : 'set',
    'setze_attr' : 'setattr',
    'sortiert' : 'sorted',
    'statischemethode' : 'staticmethod',
    'summe' : 'sum',
    'ober' : 'super',
    'tupel' : 'tuple',
    'typ' : 'type',
    'xintervall' : 'xrange',
}






