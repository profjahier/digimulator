Complément à 2 – Olivier Lecluse			
Lancer l’exécution à l’adresse 0			
Utiliser les boutons pour choisir un nombre			
Le complément a2 s’affiche en temps réel
			
00000000	SPEED		00000010	Vitesse d’exécution
00000001	1		00000001	
00000010	SBR		00011001	Autorise l’écriture sur les LED d’adresses
00000011	2		00000010	
00000100	statusRegister	11111100	
00000101	COPYLA		00000100	
00000110	0		00000000	Acc = 0 – dataLEDRegister  
00000111	SUBRA		00001011	L’accumulateur contient le complément à 2 de la variable dataLED
00001000	dataLEDRegister	11111111	
00001001	COPYAR		00000101	Affiche le complément à 2 sur les LED d’adresses
00001010	adrLEDRegister	11111110	
00001011	COPYRR		00000111	Sauvegarde dataLED dans la variable lastData
00001100	dataLEDRegister	11111111	
00001101	lstDataRegister	11110000	
00001110	COPYRA		00000110	Réalise un XOR entre les boutons et dataLED Afin de prendre en compte une éventuelle saisie
00001111	buttonRegister	11111101	
00010000	XORRA		00010001	
00010001	dataLEDRegister	11111111	
00010010	COPYAR		00000101	teste si un bouton a été appuyé depuis le dernier calcul Pour cela, on soustrait dataLED à lastData  
00010011	dataLEDRegister	11111111	Le if se fait selon le bit 0 du statusRegister (zeroFlag)  
00010100	SUBRA		00001011	Si aucun bouton n’a été préssé, on revient direct au début du programme 
00010101	lstDataRegister	11110000	Ce qui permet une réactivité immédiate des boutons. 
00010110	BCRSS		00011011	La boucle d’attente ne s’enclanche que si une saisie est détectée
00010111	0		00000000	
00011000	statusRegister	11111100	
00011001	CALL		00011101	Il y a eu appui de l’utilisateur Boucle d’attente pour éviter l’alternance trop rapide de la LED correspondant au bouton resté enfoncé
00011010	32		00100000	
00011011	JUMP		00011100	Retour au début du programme
00011100	5		00000101	
00011101			
00011110			
00011111			
00100000	COPYLR		00000011	Boucle d’attente de 128 tours
00100001	128		10000000	
00100010	loopTouche	11110001	
00100011	DECRJZ		00010100	
00100100	loopTouche	11110001	
00100101	JUMP		00011100	
00100110	35		00100011	
00100111	RETURN		00011111	

