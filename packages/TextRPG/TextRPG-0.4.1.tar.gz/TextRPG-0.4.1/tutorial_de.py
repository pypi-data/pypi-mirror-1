#!/usr/bin/env python
# encoding: utf-8

"""TextRPG Tutorial - Ein Leitfaden zur Nutzung des TextRPG.

Lektionen: 
 - Einleitung und Definition.
 - Erzählen und ausprobieren. 
 - Nutzer fragen und Geschichten weitergeben. 
 - Charaktere erzeugen und sprechen lassen. 
 - Proben und Wettkämpfe. 
 - Charaktere laden und speichern.
 - Kämpfe und Weiterentwicklung von Charakteren.
 - Nichtlineare Geschichten und die Möglichkeiten von Python. (auch Funktionen und auslagern)
 - Erweiterungen nutzen und selbst entwickeln.
"""

# First make sure the user has at least Python 2.5
from sys import version_info
if version_info < (2,5): 
    print "TextRPG braucht mindestens Python Version 2.5."
    print "Sie finden aktuelle Python Version auf "
    print "- http://python.org "
    exit()
elif version_info >= (3,0): 
    print "TextRPG wurde noch nicht auf Python Version 3 oder höher aktualisiert."
    print "Bitte geben Sie uns die nötige Zeit, oder tragen sie zum Portieren bei."
    print "- http://rpg-1d6.sf.net"
    exit()

from rpg_lib.textrpg import story, ask

# Idee: Den Nutzer die Möglichkeiten gleich testen lassen. 
from subprocess import call 

story("""Willkommen im Interaktiven TextRPG Tutorial!

Dieser Leitfaden wird Ihnen Schritt für Schritt die Möglichkeiten des TextRPG nahebringen und es Ihnen so ermöglichen auf einfache Art eigene TextRPGs zu schreiben. 

Erstmal zur Definition: Ein TextRPG ist eine interaktive Geschichte, in die ihre Nutzer eintauchen und ihren Ausgang beeinflussen können. 

Auch wenn es mit komplexeren Skripten wohl möglich wäre, mit dem TextRPG ein MMORPG zu implementieren, ist das nicht seine grundlegende Zielsetzung. 

Stattdessen definiert es eine einfache Skriptumgebung, mit der der Code einer interaktiven Geschichte sehr ähnlich aussieht wie ein Skript für ein Theaterstück, Sie gleichzeitig aber auf die gesamte Macht von Python zurückgreifen können, mit dem sowohl einfache Skripte, als auch komplexeste Programme geschrieben werden können (und das auch die NASA und Google nutzen).

Obwohl diese erste Version rein textbasiert ist, sind die Skripte auf eine Art geschrieben, die eine spätere Uebertragung in graphische Oberflächen einfach macht, so dass in den Skripten nur eingefügt werden muss, welche Oberfläche sie nutzen sollen. Das gleiche gilt für sonstige Erweiterungen. 

Für Charakterinteraktionen gibt sie Ihnen ausserdem eine vollständige RPG Bibliothek, die das Ein Würfel System implementert, ein universelles und frei lizensiertes Rollenspielsystem. 

Da das TextRPG in Python geschrieben wurde, funktioniert es direkt auf den verschiedensten Plattformen, GNU/Linux, MacOSX und Windows eingeschlossen. 

Dieser Leitfaden ist übrigens auch als TextRPG realisiert (öffnen Sie ihn doch mal in einem Texteditor, um den Code zu sehen). 

Nun aber genug der Vorrede. Gehen wir zur ersten Lektion. 
""")

story("""= Lektion 1: Erzählen und direktes Ausprobieren des Gelernten =

Um Ihnen die Eingänglichkeit der Skriptsprache zu zeigen, möchte ich Ihnen vor jeglichem Anderen zeigen, wie sie einen Text zeigen können.

Für einfache Texte können sie die Funktion story('''text''') nutzen. 

Ein Beispiel: Nehmen wir an, sie wollten ein Gedicht wie das folgende zeilenweise anzeigen: 

Träume in Texten
Welten in Träumen
Menschen in Welten
In eigenem Traum. 

Sie schaffen sich eigene Texte. 

Um dieses Gedicht in einem TextRPG anzuzeigen nutzen sie die story() Funktion: 

story('''Träume in Texten
Welten im Träumen
Menschen in Welten
In eigenem Traum

Sie schaffen sich eigene Texte.''')

Wie das funktioniert, können sie gleich direkt ausprobieren, denn sobald diese Lektion abgeschlossen ist, wird sich direkt im Text der Python Interpreter öffnen. 

Auch wenn der Name "Interpreter" etwas kompliziert klingt, ist das für was Sie ihn nutzen können extrem einfach: 

Sie können Code eingeben und sehen sofort was er bewirkt.

Dass sie im Interpreter sind, erkennen sie (unter anderem) daran, dass die Textzeile mit '>>> ' anfängt. 

Wenn sie Code schreiben, der sich über mehrere Zeilen erstreckt (wie sie es z.B. bei story() gesehen haben), ändert sich der Zeilenanfang in '... '. 

Um den Interpreter wieder zu verlassen und mit diesem Leitfaden fortzufahren, geben sie einfach exit() ein, d.h. sie tippen "exit()" und drücken dann die Enter-Taste zur Bestätigung. 

Wenn sich nun gleich der Interpreter öffnet, geben sie, um Ihre TextRPG Kenntnisse zu testen, als erstes das folgende ein (ohne '>>> '): 
>>> from rpg_lib.textrpg import *

Damit können sie dann die Funktionen des TextRPG nutzen, z.B. story(). 

Als nächsten Schritt rufen sie wie bereits beschrieben die Funktion story() auf: 

story('''Träume in Texten, 
Welten in Träumen
Menschen in Welten
In eigenem Traum. 

Sie schaffen sich eigene Texte.
''')

Als Abschluss, verlassen sie den Python Interpreter mit exit() und Enter zur Bestätigung.

Wir wechseln nun in den Python Interpreter. """)

call("python")

story("""= Lektion 2: Dem Nutzer Fragen stellen und Geschichten weitergeben =

Der zweite Schritt zu komplexeren Geschichten ist grundlegende Interaktion mit dem Benutzer, genauer gesagt: Dem Benutzer Fragen stellen. 

Mit dem TextRPG können Sie das einfach auf die folgende Art und Weise tun: 

ask('''Frage? (Antwort 1, antwort 2, ...) ''')

ask liefert die Antwort des Benutzers zurück. In obigem Beispiel verfällt sie allerdings. Damit Sie mit ihr arbeiten können müssen Sie diese Antwort noch auffangen. Beispielsweise können Sie sie als antwort speichern: 

antwort = ask('''Frage? (Antwort 1, antwort 2, ...)''')

Um nun zu prüfen, ob antwort einen bestimmten Wert hat, nutzen Sie am einfachsten "if", "elif" und "else". 
Ein Beispiel (was es tut werde ich danach beschreiben): 

if antwort.lower() in ["jupp", "jau", "j", ""]: 
    story('''Gerne!''')
elif antwort.lower() in ["vielleicht", "kann sein", "v"]: 
    story('''Mmh, muss ich noch drüber nachdenken.''')
else: 
    story('''Vergiss es. Honig kriegt nur, wer auch Bienen pflegt.''')

Was dieser Code tut, ist das folgende; doppel-zeilenweise beschrieben: 

if antwort.lower() in ["jupp", "jau", "j", ""]: 
    story('''Oh ja!''')

prüft ob die in Kleinbuchstaben konvertierte Antwort (".lower()" übernimmt die Konvertierung in Kleinbuchstaben) einer der Werte in '["jupp", "jau", "j", ""]' ist, also ob die Antwort in Kleinbuchstaben entweder "jupp", "jau", "j"  oder leer ("") ist. 
In dem Fall ruft sie story() mit dem Wert '''Gerne!''' auf. 

Gibt der Nutzer keine Antwort, sondern drückt einfach Enter, dann gilt das als "", also eine leere Antwort. Diesen Wert können Sie sehr einfach nutzen, um die Standardantwort zu wählen. 
Nach Konvention wird die Standardantwort bei Fragen groß geschrieben und der Rest klein. 

Der Doppelpunkt bei "if ... :" und die Einrückung von story() zeigen in TextRPG Skripten an, dass story('''Oh Ja!''') zu dem Block der if Abfrage gehört. Wo es wieder zur ursprünglichen Einrückung zurück geht (bei elif) ist der if-block beendet. 

Technisch gesehen ist '["jupp", "jau", "j", ""]' eine Liste, und die Abfrage 'antwort.lower() in ["jupp", "jau", "j", ""]' prüft, ob der Wert von antwort.lower() in der Liste steht. 

Ist das der Fall werden alle elif und else, die direkt danach kommen, ignoriert und die Geschichte springt über sie hinweg. 

Ist 'antwort.lower' aber nicht 'in ["jupp", "jau", "j"]', prüft Python, ob nach der if Abfrage ein elif oder ein else kommt. 

In unserem Fall folgt ein elif: 

elif antwort.lower() in ["vielleicht", "kann sein", "v"]: 
    story('''Mmh, muss ich noch drüber nachdenken.''')

Dieses elif bedeutet: Wenn die if Abfrage vorher nicht zutraf, prüfe, ob die elif Abfrage stimmt ("elif" ist die Kurzform für "else if"). 

Das heißt: Wenn der Nutzer nicht "jupp", "jau" oder "j" geantwortet hat, prüfe, ob er "vielleicht", "kann sein" oder "v" geschrieben hat. 
Hat er das, wird '''Mmh, muss ich noch drüber nachdenken.''' ausgegeben. 

Trifft allerdings auch das nicht zu, läuft der Code weiter und Python trifft auf das 

else: 
    story('''Vergiss es. Honig kriegt nur, wer auch Bienen pflegt.''')

Das heißt nun: Wenn die Antwort auf alle vorigen nicht passt, schreibe '''Vergiss es. Honig kriegt nur, wer auch Bienen pflegt.'''

Es kann pro "if" nur ein "else" geben, und ein "else" beendet den if/elif/else Block (genauso wie eine leere Zeile oder ein neues "if"). 

Kurzformen für Antworten, z.B. der erste Buchstabe des Wortes, erleichtern oft das Erleben der Geschichte deutlich. 

Natürlich kann dabei statt "antwort" auch eine spezifischere Bezeichnung gewählt werden, z.B. 

bereit_bienen_zu_pflegen = ask('''Würdest du dich für das Glas Honig um meine Bienen kümmern, während ich weg bin? (Jupp, vielleicht, nein)''')

Und diese Antwort kann auch immer wieder genutzt werden, also kann auch später im Spiel immer wieder gefragt werden: 

if bereit_bienen_zu_pflegen.lower() in ["ja", "jupp", "j", ""]: 
    story('''Du findest noch ein Glas Honig im Schrank, für das dir Ogame sicher interessante Neuigkeiten erzählen wird.''')

Sie können die Antwort erst dann nicht mehr nutzen, wenn Sie sie mit einer anderen Antwort überschrieben haben. Zum Beispiel könnten Sie die Frage erneut stellen: 

bereit_bienen_zu_pflegen = ask('''Würdest du nochmal die Pflege meiner Bienen übernehmen? (Jupp, vielleicht, nein)''')

Jetzt enthält bereit_bienen_zu_pflegen die neue Antwort, aber nicht mehr die Alte. 
""")

test_in_interpreter = ask("Wollen Sie das gleich im Interpreter testen?  (Ja, nein)")

if test_in_interpreter.lower() in ["ja", "j", ""]: 
    story("""Der Python Interpreter wird gleich gestartet. Denken sie daran vor ihrem Code 
from rpg_lib.textrpg import * 
einzugeben. 

Wie üblich können Sie ihn mit exit() verlassen, um mit dem zweiten Teil von Lektion 2 fortzufahren.""")
    call("python")


story("""Und hiermit können Sie bereits vollständige interaktive Geschichten erzählen (auch wenn Sie vieles noch mit Handarbeit erledigen müssen), so dass ich nun zum zweiten Teil dieser Lektion komme: Wie Sie Ihre eigenen Geschichten an andere weitergeben können. 

Sie haben bereits mit dem Python Interpreter experimentiert und dabei vielleicht schon den Code für kleinere eigene Geschichten geschrieben. Um die Geschichten weiterzugeben, müssen Sie nur diesen selbstgeschriebenen Code in eine Textdatei kopieren, die mit den folgenden Zeilen anfängt: 

------ Der Anfang Ihrer Textdatei ------
#!/usr/bin/env python
# encoding: utf-8

from rpg_lib.textrpg import *
------ Hier könnte Ihr Code folgen ------

Was die Zeilen bewirken:

Die erste Zeile (#!/usr/bin/env python) bewirkt auf GNU/Linux und MacOSX, dass die Datei wie jedes andere Programm staret, wenn sie (doppelt) angeklickt wird.

Technisch: das Programm /usr/bin/env ruft das Programm python auf, um die Datei zu öffnen. 
/usr/bin/env wird verwendet, weil python nicht in jedem System an der gleichen Stelle installiert ist. /usr/bin/env weiß allerdings, wo es liegt.

Die zweite Zeile (# encoding: utf-8) sagt, dass Ihre Textdatei in utf-8 kodiert ist, sie also Umlaute u.ä. nutzen können. 

Die dritte Zeile ist nur für die Lesbarkeit da und einfach leer. 

Die vierte Zeile (from rpg_lib.textrpg import *) gibt Ihnen Funktionen, die Sie für das Schreiben Ihrer eigenen Geschichte nutzen können. 

Technisch bedeutet sie: "Hole alle Funktionen (* holt alles) aus lib.textrpg in meine Datei, so dass ich sie direkt aufrufen kann."

Unter diesen vier Zeilen können Sie nun direkt den Code Ihrer Geschichte schreiben. 

Um die Geschichte an einem bestimmten Punkt beenden zu können (z.B. bei '''ob Sie nun dort warten oder nicht'''), können Sie die Funktion "exit()" verwenden. Sie stoppt die Geschichte. 

Also könnte die Datei zum Beispiel so aussehen: 

------ Eine Geschichte ------
#!/usr/bin/env python
# encoding: utf-8

from rpg_lib.textrpg import *

story('''Kaum ein Schimmer von Licht dringt durch das Blätterdach der düsteren Bäume, und der schmale Pfad auf dem du läufst wird mehr und mehr zu einem Wildweg, mehr für Hasen und Wölfe geeignet, als für Menschen. 

Kein Vogelzwitschern erfüllt die Luft, so dass nur deine Schritte im trockenen Laub die Stille durchdringen, doch an Umkehr wagst du nicht zu denken, denn hinter dir warten Sie. 

Deine Beine tragen dich weiter, und du beginnst ein dunkles Brummen zu hören, das mit jedem Schritt lauter wird und dich zu umfangen scheint, wie Gewebe, das alle anderen Geräusche verdrängt. ''')

weitergehen = ask('''Willst du weitergehen? (Ja, nein)''')

if weitergehen.lower() in ["ja", "j", ""]: 
    story('''Du gehst tiefer in den Wald, während das Brummen Stück für Stück nicht nur die Geräusche, sondern jeden deiner Gedanken verdrängt. 

Du kannst nicht abschätzen, wie lange du bereits läufst, als das Brummen plötzlich abschwillt und eine Gestalt auf dem Pfad vor dir auftaucht. Noch bevor du sie richtig erkennst, hörst du ihren Ruf: Sei gegrüßt Fremder. Sei mein Gast für diese Nacht!''')
else: 
    story('''Du bleibst stehen, bis dein Hunger dich zwingt, den Rückweg anzutreten, ob Sie nun dort warten oder nicht.''')
    exit()

exit()
------ Ende des Anfangs ------

Als Versuch können Sie den obigen Geschichtsanfang in eine Textdatei kopieren, die Textdatei ausführbar machen, sie in den Ordner neben die Datei dieses Tutorials legen und sie dann anklicken. 

Wenn Sie sie anderen geben wollen, muss neben ihr außerdem der Ordner "lib" liegen, der auch bei diesem Tutorial liegt. Also könnten Sie sie in einem Ordner weitergeben, der zum Beispiel so aussieht: 

mein_spiel/
    mein_spiel.py
    lib/

Um die Geschichte zu starten, muss der Nutzer nun einfach mein_spiel.py (doppelt) anklicken. 

Im gleich startenden Python Interpreter können Sie einfach Abschnitte Ihrer eigenen Geschichte ausprobieren, bevor Sie sie in die Textdatei schreiben. Um ihn zu verlassen, benutzen sie wie üblich exit(). 
Damit kommen wir zum Ende von Lektion 2. Viel Spaß beim experimentieren! """)

call("python")

story("""Lektion 3: Charaktere erzeugen und sprechen lassen.

In Arbeit. 

""")