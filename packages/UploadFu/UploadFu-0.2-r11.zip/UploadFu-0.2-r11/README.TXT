Cerinte:
    - http://downloads.activestate.com/ActivePython/windows/2.5/ActivePython-2.5.1.1-win32-x86.msi
    - un creier (adica stii sa rulezi 2 comenzi in consola si sa editezi un fisier de configurare) - nu vreau sa devin un "master of the obvious" si sa explic banalitati
    
Ce face:
    Upload din meniul contextual al directoarelor pe baza unor fisiere de configuratie. 
    Scriptul creaza fisierul torrent, il incarca pe tracker cu setarile din fisierul .ini, 
descarca torentul si il incarca in clientul de torent - in alte cuvinte e un fel de "2-click upload"
    
    Se pot folosi mai multe fisiere de configuratie.
    Se poate folosi cu mai multe directoare (torrent batching)
    Exista niste limite in sistemul de operare si nu se pot incarca torente care au caile cumulate mai lungi de 32767 caractere - in alte cuvinte nu mai mult de 500 (estimat).
    
    
Instalare:

- se deface arhiva 
- se ruleaza install.bat
- se editeaza X:\Python25\Scripts\iplay.ini
    - se modifica locurile unde scrie [snip], adica parola, useru, passkey
    - daca difera ceva se poate edita
    - la sectiunea [upload] sunt setarile de upload
    - am gandit programu sa foloseasca mai multe fisiere de 
    configurare, deci daca incarci in mai multe categorii ai nevoie de mai multe fisiere de configurare
- se foloseste meniul contextual

Note:

- teoretic ar trebui sa mearga si cu alte trackere, cu mici adjustari in script poate.
- USE AT YOUR OWN RISC :)


Author: Leonord