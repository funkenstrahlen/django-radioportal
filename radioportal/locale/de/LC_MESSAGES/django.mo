��    �          �             �     a  �  >  K  �   �  �   Y  h     �   w  �   F               '  "   8     [  $   t  $   �    �  1   �  +        4     :     B     S     e     w     �     �     �     �     �     �                    .  �   F  "   �  $   �          #     0     <  J   H  ?   �  5   �     	          ,  B   ?  -   �  K   �  6   �     3     ;     J     Y     i     }     �  1   �     �     �     �     �     �  	                  4     I     P     T  6   ]     �     �     �  $   �     �     �     �  +         1      9      @   �   Q      �      �      !     "!     :!  <   U!  -  �!     �#     �#     �#     �#     �#     �#  /   $  *   6$     a$     r$     �$     �$  &   �$     �$     �$     �$  %   %     4%     B%     ]%     f%     k%     %     �%     �%     �%     �%     �%  
   �%  	   �%     �%     �%  	   &      &     :&     U&     c&     s&     �&     �&  	   �&  
   �&  	   �&  $   �&     �&     �&     �&     '     '     '     !'     ''     E'  "   d'     �'     �'     �'  J   �'  T   (  (   b(     �(  c   �(  =   �(     3)     G)  )   K)  Q   u)  .   �)     �)     �)     *     "*     4*  }   R*     �*  	   �*    �*  :   �+     .,     @,     G,     N,     S,     \,     a,     f,     l,     o,     r,     �,  &   �,     �,     �,      �,     �,  �   �,     �-  j  �-  g  >/    �0  }  �1  o  A3  	  �4  �   �5  f   �6    7  �   8     �8     �8     	9  #   $9     H9     b9  %   �9  (  �9  3   �:  5   ;     9;     B;     I;     [;     n;     �;     �;     �;     �;     �;     �;      <      <     '<     8<     T<  �   m<  <   j=  $   �=     �=     �=     �=     >  R   >  ]   i>  Y   �>     !?     8?     N?  S   e?  L   �?  R   @  ;   Y@     �@     �@     �@     �@     �@     �@     �@  5   
A     @A     LA  
   RA     ]A     pA     �A     �A  $   �A  $   �A  
   �A     B     
B  &   B     8B     TB     fB  1   lB     �B     �B  !   �B  .   �B     �B     C     	C  �   C     �C     �C     �C     �C     �C  A   �C  �  =D     �F     �F     �F     �F     �F     �F  /   G  -   <G     jG     {G     �G     �G  )   �G     �G     �G  "   H  +   .H     ZH     mH  
   �H     �H     �H     �H     �H     �H     �H     �H      I     I     I      I     3I     NI  "   [I  '   ~I     �I     �I     �I     �I     �I     �I      J     J  !   J     <J     LJ     TJ  	   oJ     yJ     ~J     �J     �J  ,   �J  )   �J     K     K     9K  Y   RK  h   �K  #   L     9L  x   ?L  O   �L     M     M  ,    M     MM  �  �M     �P     �P     �P     �P  &   �P  �   �P     nQ     uQ  '  �Q  P   �R     S     S     S  
   $S  	   /S     9S     =S  	   JS     TS     XS     \S     wS  -   �S     �S     �S     �S     �S  �   �S     �T     Y   >       D   *   V   X   �   �          �       �   2          �      �   �      /      R       0       9   �   g       |   }   �   ~               �       �   q          1         �   �   �       +   N               4      �   �   �   a               L   &   w   �   �                        @   �   U   \       7       [       �           M   8   �   {       �   �   Z                   C   F      �   �   =   G       %   �           �   r   y   j   �   S       '          �           ;   �   ^       3   	       c       ]   !   �   �   t   �   I   �   �   #       �   b       -   x       .   6   K       �             �   �   f       �       �          m       o      n           J   �                   �   �   s   �   �   �   �   
   Q            W   �   P   �   �   $          u       d   B      �   �   �             �          k   h   <      �      5          �   (   `               O       �   �   T   �   v   ?   :   e   "   ,   i   )   �       _   H   A   �   E       z   l   p    
Auphonic notifications are used to create a production based on the selected preset, upload the currently available recording to Auphonic and start
the production if desired.
The start, stop and rollover templates are used for filling in the title tag of the production.
 
For every show there is usually a channel of streams. Such a channel of streams combines various streams which differ in bitrates or formats. 
This is the place to view or change the credentials for your streams.
 
For the HTTP Callback Notification a HTTP POST is issued to the specified url. The evaluated content of the template is send in the
request body without any further encoding. The requests will have the User-Agent set to "xenim notification".<br />
If you need other request types, encodings or headers do not hesitate to contact info@streams.xenim.de.
 
For the templates the <a href="https://docs.python.org/2/library/string.html#format-string-syntax">Python format string syntax</a> is used. 
If an empty string is supplied for the template no notification will be send to the service for the respective event. The following variables 
are available for the templates:
 
IRC Notifications are posted as regular messages by <em>xsnBot</em>, who is currently available on FreeNode and HackInt. If you need
notifications on an other network please contact info@streams.xenim.de.
 
Shows are the entities that are responsible for representing your streams at the homepage of the xenim streaming network. 
They also contain episodes for time a stream is online.
 
The Twitter Retweet Notification will retweet the update made by selected Twitter Update Notification.
 
The properties of this show are currently updated from the configured podcast feed. If you want to change
properties of the show either update the podcast feed or disable the automatic update via the feed
 
Twitter notification will post the evaluated template to the associated account. Be aware that the evaluated template will be truncated after
the 140th character to prevent posting errors.
  from %s Abbreviation of the show Account Settings Add new HTTP Callback notification Add new IRC notification Add new Twitter Posting Notification Add new Twitter Retweet Notification An episode might be split up into several parts when for example the streams gets 
disconnected due to network problems. The parts can also be transferred to other episodes in case of wrong matching.
This is currently not possible with the webinterface, so ask the administrator. Append new episode part to generic episode "live" Application is in wrong state. Ignoring it. Apply Archive Archived Episode Archived Episodes Archived episodes Associated Graphics Associated Recordings Associated shows Auphonic Account %s Auphonic Login Name Auphonic Preset Available for template Begin Change Password Change Permissions for Channel for %(cluster)s Configure order for mapping methods. Use drop-down box for adding new items, [x] for removing items and drag&drop for changing order. Configure update from podcast feed Could not fetch matching application Create Episode Create Group Create Show Create User Create a new episode by incrementing the number of the last episode by one Create a new episode using the episodeNumber stored in the show Create an episode named live with current date suffix Create new Channel Create new Show Create new episode Create new episode using the first word of the title as episode id Create new episode using the full title as ID Create new episode, get episode number by adding one to last episode number Currently streamed episodes on xenim streaming network Default Delete Channel Delete Episode Delete Episodes Delete Notification Delete Show Description Description as specified in icecast source client Does nothing. Duration Edit Edit Channel Edit Part of Episode Edit Show Edit episode Edit show notifications Edit show properties Enable End Episodes Episodes which are scheduled to be aired in the future Example Feed of the podcast File Find or create an episode named "%s" First From Full URL to the current episode Genre as specified in icecast source client Graphic Groups HTTP Callback %s Here are informations about the shows available, which were distributed through this streaming system. This includes the graphical statistic about listener counts. Homepage Homepage of the Show IRC Channel %s IRC Network and Channel Identifier of used channel Internally used (e.g. in atom feed) slug for current episode It is possible to update the show and episode from the podcast feed of your show. 
To use this feature enable it below and enter the URL to your feed. Additionally it is necessary to 
specify a regular expression to separate the title of a feed entry into a id for an episode and the 
topic of this episode. This is used to correlate an entry from the feed with an episode of the xenim
streaming network. The regular expression should contain the two named groups "id" and "topic". An
Example for an entry like "MM073 Creepy" is "(?P<id>\w*) (?P<topic>.*)". Last Licence List of Users Listen Live Longer description of the show Method for mapping between streams and episodes Name as specified in icecast source client Name of the show New Recoded Stream New Sourced Stream Next No episodes are streamed at the moment No episodes available. No shows available. No streams available currently Notification for %(show)s on %(path)s Notifications Number of the next episode Overview Page Page of the Episode Parts of this Episode Password change Password reset Path Permissions for Previous Public URL Read more Recent Episodes Recently aired episodes Recording Regular expression for the title Retweet Notification on %s Retweet from  Running Episode Running Episodes Running episodes Save Channel Share on: Short Name Short URL Shortened URL to the current episode Should the object Show Show Notifications Shows Since Size Start Start Production after upload Stream identifier from backend Streams are upcoming, please wait. Template for rollover Template for start Template for stop The current episode can only be changed for channel with a running stream. The number of the next episode to be aired. Used to construct the episode identifier There are no episodes upcoming currently Topic Try to find an existing episode with a slug, which is the same as the first word of the stream name Try to find the earliest possible, existing, upcoming episode Twitter Account @%s URL URL as specified in icecast source client URLs to all currently available streams. Might include HLS streams in the future. USERCREATEDMAIL with %(username)s %(password)s Upcoming Upcoming Episode Upcoming Episodes Upcoming episodes Used to construct the episode Used to extract the id and title from the »title« field of the feed. Should contain the match groups »id« and »title«.  User User List Welcome to the configuration panel of the xenim streaming network. 
Here you can change all settings regarding the appearance of your show and the behavior of the streams.
You might also have a look at the wiki for additional features, documentation and contact informations. Your username and password didn't match. Please try again. archived episodes delete direct edit feed for from here login of on really be deleted running episodes show which is assigned to this channel until upcoming episodes visualization of listener counts with xenim is able to send notifications to several external services when a show starts, a new part of a show starts or when a show has finished. You can
use this page to configure this notifications.
 xsn Archive for %s Project-Id-Version: PACKAGE VERSION
Report-Msgid-Bugs-To: 
POT-Creation-Date: 2015-07-08 16:07+0200
PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE
Last-Translator: FULL NAME <EMAIL@ADDRESS>
Language-Team: LANGUAGE <LL@li.org>
Language: 
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
Plural-Forms: nplurals=2; plural=(n != 1)
 
Auphonic Benachrichtigungen werden genutzt, um eine Production auf Basis des ausgewählten Presets zu erstellen, die momentan verfügbare Aufzeichnung zu Auphonic hochzuladen und die Production zu starten, falls dies ausgewählt ist.Die Folgenstart-, Folgenende- und Folgenänderungstemplates werden genutzt, um das Feld "title" der Production zu befüllen.
 
Zu jeder Sendung gehört üblicherweise eine Sammlung von Streams. Eine solche Sammlung vereint verschiedene Streams, die sich in Format und Bitrate unterscheiden. Hier können neben den üblichen Einstellungen auch die Zugangsdaten für die Streams eingesehen und geändert werden.
 
Bei der HTTP Callback Benachrichtigung wird eine HTTP POST Anfrage an die eingestellte URL gestellt. Die ausgefüllte Vorlage wird dabei im Body der Anfrage ohne weitere Codierung mitgeschickt. Die Anfragen haben als User-Agent "xenim notification" eingestellt. Falls weitere Anfragearten, Codierungen oder HTTP Header benötigt werden bitte unter info@streams.xenim.de anfragen.
 
Für die Vorlagen wird die <a href="https://docs.python.org/2/library/string.html#format-string-syntax">format string Syntax von Python</a> benutzt. 
Falls eine Vorlage leer ist, wird für den entsprechenden Benachrichtigungsservice keine Benachrichtigung für das entsprechende Ereignis ausgelöst. Die folgenden Variablen können in den Vorlagen verwendet werden:
 
IRC Benachrichtigungen werden als normale Nachrichten durch <em>xsnBot</em> in den konfigurierten Kanal geschrieben. Der Bot ist momentan in den Netzwerken FreeNode und Hackint aktiv, falls andere Netzwerke benötigt werden bitte an info@streams.xenim.de wenden. 
 
Sendungen sind die Objekte, die dafür zuständig sind, wie die Streams auf der Webseite des xenim streaming networks dargestellt werden. Sendungen enthalten auch die Folgen, die erstellt werden, wenn ein Stream online geht.
 
Die Twitter Retweet Benachrichtigung retweetet den Tweet der ausgewählten Twitter Benachrichtigung.
 
Die Eigenschaften dieser Sendung werden momentan über den eingestellten Podcast Feed aktualisiert. Um die Einstellungen dieser Sendung zu ändern, mussentweder der Podcast Feed aktualisiert werden oder das automatische Update über den Feed deaktiviert werden:
 
Für Twitter Benachrichtigungen wird die ausgefüllte Vorlage als Update in den konfigurierten Account gepostet. Um Fehler beim Posten zu verhindern, wird die ausgefüllte Vorlage nach 140 Zeichen abgeschnitten.
  von %s Abkürzung des Sendungsnamens Einstellungen für Account Neue HTTP Callback Benachrichtigung Neue IRC Benachrichtigung Neue Twitter Benachrichtigung Neue Twitter Retweet Benachrichtigung Eine Folge kann in Teile mehrere Teile unterbrochen werden, wenn beispielsweise der Stream aufgrund von Netzwerkproblemen abbricht.<br />Die Teile können auch anderen Folgen zugeordnet werden. Dies ist momentan nicht über das Webinterface möglich, bei Bedarf bitte an den Administrator wenden. Hänge neue Teilfolge an generische Folge "live" an Anfrage hat falschen Status und wird nicht verwendet. Anwenden Archiv Archivierte Folge Archivierte Folgen Archivierte Folgen Zugehörige Grafiken Zugehörige Aufzeichnungen Zugeordnete Sendungen Auphonic Account @%s Auphinic Login Name Auphonic Preset Verfügbar in den Vorlagen für Anfang Passwort ändern Zugriffsrechte ändern für Channel für %(cluster)s Methoden zur Zuordnung von Stream zu angekündigten Folgen konfigurieren. Mit der Drop-Down-Box können Methoden hinzugefügt werden, mit drag&drop kann die Reihenfolge verändert werden und mit × können Methoden wieder aus der Liste entfernt werden. Konfiguriere Aktualisierung der Sendung aus dem Podcast Feed Konnte keine passende Anfrage laden. Neue Folge ankündigen Erstelle Gruppe Sendung erstellen Nutzer erstellen Erstelle neue Folge, nehme alte Folgennummer inkrementiert um eins als neue Nummer Erstelle neue Folge, nutze Folgennummer aus der ersten Sendung die dem Channel zugeordnet ist Erstelle neue Folge und nutze "live" gefolgt von dem aktuellen Datum und Uhrzeit als Slug Erstelle neuen Channel Erstelle neue Sendung Neue Folge ankündigen Erstelle neue Folge und nutze das erste Wort des Feldes "Name" des Streams als Slug Erstelle neue Folge und nutze das komplette Feld "Name" des Streams als Slug Erstelle neue Folge, nehme alte Folgennummer inkrementiert um eins als neue Nummer Momentan über das xenim streaming network gesendete Folgen Voreinstellung Channel löschen Folge löschen Lösche Folgen Lösche Benachrichtigung Sendung löschen Beschreibung Beschreibung wie im Icecast Source Client eingetragen Tut nichts. Dauer Bearbeiten Channel bearbeiten Teil der Sendung bearbeiten Sendung bearbeiten Folge bearbeiten Bearbeite Sendungsbenachrichtigungen Einstellungen der Sendung bearbeiten Aktivieren Ende Folgen Folgen deren Ausstrahlung geplant ist. Beispielinhalt der Variable Feed des Podcasts Datei Finde oder Erstelle eine Folge mit dem Namen "%s" Anfang Von Komplette URL zur aktuellen Folge Genre wie im Icecast Source Client eingetragen Grafik Gruppen HTTP Callback %s Hier gibt es Informationen und die grafischen Darstellungen der Hörerzahlender Sendungen, die über dieses Streamingsystem verbreitet wurden. Webseite Webseite der Sendung IRC Kanal %s IRC Netzwerk und Kanal ID des Channels Intern genutzter Slug (z.B. im Atom Feed) für die aktuelle Folge Es ist möglich die Sendung und die zugehörigen Folgen über den Podcast Feed zu aktualisieren.Um dieses Feature zu nutzen, muss es unten aktiviert werden, es muss die URL des Podcast Feeds eintragen und ein Regulärer Ausdruck angeben werden. Der Reguläre Ausdruck dient dazuden Titel eines Eintrages im Feed in eine ID für eine Episode und einen Titel zu zerlegen. Die ID wirdanschließend verwendet, um den Feed Eintrag einer Folge zuzuordnen. Der Reguläre Ausdruck sollte die beiden named groups "id" und "topic" enthalten. Wenn der Titel im Feed beispielsweise "MM073 Creepy" lautet, ist ein passender Ausdruck "(?P<id>\w*) (?P<topic>.*)". Ende Lizenz Liste der Benutzer Hören Live Ausführliche Beschreibung Algorithmus zur Zuordnung von Folgen zu Streams Name wie im Icecast Source Client eingetragen Name der Sendung Neuer Recoded Stream Neuer Sourced Stream Weiter Es werden momentan keine Folgen gesendet. Keine Folgen verfügbar. Keine Sendungen verfügbar. Momentan keine Streams verfügbar. Benachrichtigung für %(show)s auf %(path)s Benachrichtigungen Nummer der nächsten Folge Übersicht Seite Webseite zur Folge Teile dieser Folge Passwort ändern Passwort zurücksetzen Pfad Zugriffsrechte für Zurück Öffentliche URL Weiter Archivierte Folgen Kürzlich gesendete Folgen Aufzeichnung Regulärer Ausdruck für den Titel Twitter Retweet Benachrichtigung auf %s Retweet von  Laufende Folge Laufende Folgen Laufende Folgen Speichere Channel Teilen auf: Abgekürzter Name KurzURL Gekürzte URL zur aktuellen Folge Soll das Objekt Sendung Sendungsbenachrichtigungen Sendungen Seit Größe Start Starte Production nach Upload Kennung des Streams (für internen Gebrauch) Streams werden vorbereitet, bitte warten. Template für Folgenänderung Template für Folgenstart Template für Folgenende Die aktuelle Folge kann nur geändert werden, wenn ein Stream für diesen Channel läuft. Nummer der nächsten gesendeten Folge. Wird verwendet, um den Bezeichner einer neuen Folge zu erstellen. Momentan sind keine Folgen geplant. Thema Finde existierende Folge, die geplant ist und deren Slug mit dem ersten Wort des Feldes "Name" im Stream übereinstimmt. Finde existierende Folge, die geplant ist und den frühesten Startzeitpunkt hat Twitter Account @%s URL URL wie im Icecast Source Client eingetragen URLs zu allen momentan verfügbaren Streams. Diese Variable kann in zukünftigen Versionen von xenim auch HLS Streams enthalten Hallo,

soeben wurde ein neuer Account für das xenim streaming network für dich erstellt.
Mit den folgenden Zugangsdaten:
	Nutzer:   %(username)s
	Passwort: %(password)s
kannst du dich im Dashboard [1] einloggen. Dort kannst und solltest du alle 
weiteren Angaben zu deiner Sendung ergänzen bzw. ändern. Im Dashboard können 
auch die Zugangsdaten für den zentralen Icecast-Server nachgeguckt werden. 
Weitere Informationen befinden sich im Wiki [2].

Bei Fragen einfach über einen der bekannten Kanäle [3] melden.


Viele Grüße,
Das xenim streaming team

[1] https://dashboard.streams.xenim.de/dashboard/
[2] https://wiki.streams.xenim.de/
[3] https://wiki.streams.xenim.de/project/communication Geplant Geplante Folge Geplante Folgen Geplante Folgen Wird verwendet, um Folgen zu erstellen Wird verwendet, um die ID der Folge und den Titel aus dem Feed zu separieren. Sollte die Gruppen »id« und »title« enthalten. Nutzer Liste der Benutzer Willkommen auf den Konfigurationsseiten des xenim streaming networks. Hier können alle Einstellungen bezüglich der Erscheinung der Sendungen und des Verhaltens der Streams geändert werden. Im Wiki finden sich Informationen zu weiteren Features sowie allgemeine Dokumentation und Kontaktdaten. Der Nutzername und das Passwort passen nicht zueinander, bitte erneut versuchen. archivierte Folgen löschen direkt bearbeiten Feed für von Deaktivieren Einloggen von auf wirklich gelöscht werden? laufende Folgen Sendungen, die diesem Channel zugeordnet sind bis geplante Folgen Visualisierung der Hörerzahlen mit xenim kann Benachrichtigungen zu einigen externen Diensten senden, wenn eine Folge beginnt, ein neuer Teil der Folge beginnt oder eine Folge endet. Im Folgenden können diese Benachrichtigungen konfiguriert werden.
 xsn Archiv für %s 