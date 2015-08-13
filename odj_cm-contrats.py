#Extraire les contrats de l'ordre du jour du Conseil municipal
#Version 1.0, 2015-08-11
#Développé en Python 3.4
#Licence CC-BY-NC 4.0 

#Mettre les fichiers requis pour le traitement dans C:\contrats

#Fichier PDF de l'ordre du jour (17 août 2015): http://ville.montreal.qc.ca/portal/page?_pageid=5798,85945578&_dad=portal&_schema=PORTAL
#Attention, le fichier faire 250Megs

#Convertir le PDF en TXT avec pdf2txt, en Python 2.7
#Extraire que les pages 6 à 15 portant sur les contrats
#python pdf2txt.py -p 6,7,8,9,10,11,12,13,14,15 -o odj.txt -c utf-8 odj.pdf

#Fonction stripBOM
def stripBOM(fileName):
    try:
        with open(fileName, encoding='utf-8', mode='r') as f:
            reading = []
            for line in f:
                    line=line.replace('\ufeff',"")
                    reading.append(line)
                    for rest in f:
                            reading.append(rest)
        with open(fileName, encoding='utf-8', mode='w') as f:
            for line in reading:
                    f.write(line)
    except:                                         #À bonifier pour une meilleure gestion des erreurs
        print("Erreur dans stripBOM. Ne peut pas ouvrier le fichier:" + fileName)

#Fonction epurerLigne
def epurerLigne(texte):
    try: 
        reponse = str(texte).strip('[]')            #Épuration du texte extrait de l'ordre du jour
        reponse = mid(reponse,1,len(reponse)-2)     #Enlever les guillements au début et à la fin
        reponse = reponse.replace("  "," ")         #Pour une raison inconnu, il y a plusieurs 2 espaces consécutifs dans l'ordre du jour
        reponse = reponse.replace(" , ",", ")       #Pour une raison inconnu, il y a plusieurs virgules précédées d'un espace
        reponse = reponse.replace(";"," ")          #Enlever les ; pour éviter des problème avec le CSV qui sera généré     
        return reponse
    
    except:                                         #À bonifier pour une meilleure gestion des erreurs
        print("Erreur dans epurerLigne pour:" + texte )
        pass

#Fonction getNo_appel_offres
#Le numéro est toujours précédé de "offres public " et suivi par le nombre de soumissionaires entre parenthèses
def getNo_appel_offres(texte):
    try: 
        no_appel_offre = ""
        
        if len(texte) > 0:
            if texte.find("offres public ") != -1:
                debut_no_appel_offre = texte.find("offres public ") + 13
                fin_no_appel_offre = texte.find(" (", debut_no_appel_offre)
                no_appel_offre = mid(texte, debut_no_appel_offre + 1, fin_no_appel_offre - debut_no_appel_offre)
                no_appel_offre = no_appel_offre.strip()
                
        return no_appel_offre
    
    except:                                         #À bonifier pour une meilleure gestion des erreurs
        print("Erreur dans getNo_appel_offres pour:" + texte )
        pass

#Fonction getNbr_soumissions
#Le nombre de soumissions se trouve toujours après "offres public ", entre parenthèses
def getNbr_soumissions(texte):
    try: 
        nbr_soumissions = ""
        
        if len(texte) > 0:
            if texte.find("offres public ") != -1:
                debut_no_appel_offre = texte.find("offres public ") + 13
                debut_nbr_soumission = texte.find(" (", debut_no_appel_offre)
                if debut_nbr_soumission > -1:
                    fin_nbr_soumission = texte.find(" soum.)", debut_nbr_soumission)
                
                nbr_soumissions = mid(texte, debut_nbr_soumission + 2, fin_nbr_soumission - debut_nbr_soumission - 2)
                nbr_soumissions = nbr_soumissions.strip()
                
        return nbr_soumissions
    
    except:                                         #À bonifier pour une meilleure gestion des erreurs
        print("Erreur dans getNo_appel_offres pour:" + texte )
        pass
        
#Fonction getDepense_totale
#Si le terme «Dépense total» est présent, extraire le montant.
#Ceci ne couvre pas tous les cas, mais est une première étape.
#Voir si un REGEX serait plus efficace.

#DOIT ETRE RETRAVAILLÉ
def getDepense_totale(texte):
    try: 
        print("---")
        print(texte)
    
        depense_total = ""
        
        if len(texte) > 0:
            
            depense_total = 1
            print(texte.find("somme"))
            if texte.find("somme") != -1:
                depense_total = 2
                debut_depense_total = texte.find("somme") + 7
                #fin_depense_total = texte.find(" /$", debut_depense_total)
                depense_total = mid(texte, debut_depense_total + 1, 10)
                #depense_total = depense_total.strip()
                depense_total = depense_total.replace(" ", "")
        
        print(depense_total)        
        return depense_total
    
    except:                                         #À bonifier pour une meilleure gestion des erreurs
        print("Erreur dans getDepense_totale pour:" + texte )
        pass
        
#Fonction left
def left(s, amount = 1, substring = ""):
    try:
        if (substring == ""):
            return s[:amount]
        else:
            if (len(substring) > amount):
                substring = substring[:amount]
            return substring + s[:-amount]
    except:                                         #À bonifier pour une meilleure gestion des erreurs
        print("Erreur dans left:" + s )
        pass 
 
#Fonction mid
def mid(s, offset, amount):
    try:
        return s[offset:offset+amount]
    except:                                         #À bonifier pour une meilleure gestion des erreurs
        print("Erreur dans left:" + s )
        pass 
        
#Fonction right
def right(s, amount = 1, substring = ""):
    try:
        if (substring == ""):
            return s[-amount:]
        else:
            if (len(substring) > amount):
                substring = substring[:amount]
            return s[:-amount] + substring    
    except:                                         #À bonifier pour une meilleure gestion des erreurs
        print("Erreur dans left:" + s )
        pass 
        
import csv      #Pour sauvegarder les résultats dans le fichier verification.csv
 
#Début du traitement 
try:
    #Initialisation des variables
    fichier_ordre_du_jour = "C:\\contrats\\odj_cm.txt"        #Emplacement du fichier du l'ordre du jour
    date_rencontre = "2015-08-17"                   #À changer
    prefixe_decision = "20."                        #À changer au besoin
    no_decision = ""
    pour = ""
    no_dossier = ""
    no_appel_offre = ""
    debut_no_appel_offre = ""
    fin_no_appel_offre = ""
    depense_totale = ""
    texte_contrat = ""
    
    #Enlever le BOM au début du fichier
    stripBOM(fichier_ordre_du_jour)
    
    #Ouverture du fichier pour les résultats
    contrats_traites = open('contrats_traites.csv', "w", encoding="utf-8")      
    fcontrats_traites = csv.writer(contrats_traites, delimiter = '|') 
    fcontrats_traites.writerow(["instance", "date_rencontre", "no_decision", "no_dossier", "no_appel_offres", "nbr_soumissions", "depense_total", "pour", "texte_contrat"])
    
    #Passer au travers de l'ordre du jour
    with open(fichier_ordre_du_jour, 'r', encoding = 'utf-8', ) as ffichier_ordre_du_jour:
        reader = csv.reader(ffichier_ordre_du_jour, delimiter = '|')
    
        for ligne in reader:

            ligne2 = epurerLigne(ligne)
            print(ligne2)                           #Affichage à l'écran
            
            #Début d'une décision
            if left(ligne2,3) == prefixe_decision:  #Voir à utiliser uh regex à la place
            
                #Écrire le dernier contrat dans le fichier contrats_traites.txt
                if no_decision != "":      #Dans le traitement, sur la première décision, il n'y a encore rien à écrire
                    no_appel_offre = getNo_appel_offres(texte_contrat)
                    nbr_soumissions = getNbr_soumissions(texte_contrat)
                    #depense_totale = getDepense_totale(texte_contrat)
                    #fcontrats_traites.writerow(["Conseil municipal", date_rencontre, no_decision, no_dossier, no_appel_offre, nbr_soumissions, depense_totale, pour, texte_contrat])
                    fcontrats_traites.writerow(["Conseil municipal", date_rencontre, no_decision, no_dossier, no_appel_offre, nbr_soumissions, pour, texte_contrat])
                
                no_decision = ligne2        #Nouveau numéro de décision
                pour = ""                   #Initaliser le pouyr
                no_dossier = ""             #Initaliser le numéro de dossier
                no_appel_offre = ""         #Initaliser le numéro d'appel d'offre
                debut_no_appel_offre = ""
                fin_no_appel_offre = ""
                #depense_totale = ""
                texte_contrat = ""          #Initaliser le texte du contrat
            
            if left(ligne2,2) != "20":
                if len(ligne2) > 0:
                    if no_dossier != "":                        #Ne pas mettre le 'pour' dans le texte du contrat
                        if texte_contrat == "":
                            texte_contrat = ligne2.strip()      #C'estlde début du texte du contrat, évite d'avoir un espace au début
                        else:    
                            texte_contrat = texte_contrat + " " + ligne2.strip()
            
                    if no_dossier == "":                        #la variable pour est l'entité à qui le contrat
                        pour = pour + ligne2.strip()
            
                    if len(ligne2) > 9:
                        if right(ligne2,10).isnumeric():        #Voir à utiliser un regex à la place
                            no_dossier = right(ligne2,10)
                            pour = left(pour,len(pour)-14)
                            
            
    #Écrire le dernier contrat
    no_appel_offre = getNo_appel_offres(texte_contrat)
    nbr_soumissions = getNbr_soumissions(texte_contrat)
    #depense_totale = getDepense_totale(texte_contrat)
    #fcontrats_traites.writerow(["Conseil municipal", date_rencontre, no_decision, no_dossier, no_appel_offre, nbr_soumissions, depense_totale, pour, texte_contrat])
    fcontrats_traites.writerow(["Conseil municipal", date_rencontre, no_decision, no_dossier, no_appel_offre, nbr_soumissions, pour, texte_contrat])
            
#Gestion des erreurs (à bonifier)    
except  Exception as e:
    import traceback, os.path
    top = traceback.extract_stack()[-1]
    print(', '.join([type(e).__name__, os.path.basename(top[0]), str(top[1])]))
    pass

#Fermer les fichiers            
contrats_traites.close()

#Indiquer que le traitement est terminé
print()
print('-'*60)
print("Traitement terminé.")
print('-'*60)



