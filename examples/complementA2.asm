// Complement a 2
// Olivier Lecluse
// Utiliser les boutons pour choisir un nombre			
// Le complément a2 s’affiche en temps réel

%define	statusReg	 252
%define	buttonReg    253
%define	addLEDReg	 254
%define	dataLEDReg	 255
%define	zeroFlag	 0

initsp
speed 0
sbr 2 statusReg // Autorise l’écriture sur les LED d’adresses

:debut
    copyla 0 
    subra  dataLEDReg // Acc = 0 – dataLEDRegister
    copyar addLEDReg
    copyrr dataLEDReg lastData
    copyra buttonReg 
    // Réalise un XOR entre les boutons et dataLED 
    // afin de prendre en compte une éventuelle saisie
    xorra  dataLEDReg 
    copyar dataLEDReg 
    subra  lastData
    // Si aucun bouton n’a été préssé, on revient au début
    bcrss zeroFlag statusReg
    call wait
    jump debut

// Boucle d’attente de 10*255 tours sur la vraie DGR
:wait
    copylr 9 loopTouche
:waitloop
    // copylr 7 loopTouche1  // use this for digimulator
    copylr 255 loopTouche1   // use this for digirule
    :waitloop1
        decrjz loopTouche1
        jump waitloop1
    decrjz loopTouche
    jump waitloop
    return

%data lastData    0
%data loopTouche  0
%data loopTouche1 0