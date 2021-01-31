from flask import Flask, request, redirect, url_for, Response
from math import sin, cos, sqrt, atan2, radians
from datetime import timedelta
import simplejson
import json
import urllib.request
import copy
import os

#data.json tiedoston relativistinen sijainti
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
my_file = os.path.join(THIS_FOLDER, 'data.json')

#data rakenne ladattuna
with urllib.request.urlopen('http://hazor.eu.pythonanywhere.com/2021/data.json') as response:
   data = simplejson.load(response)

#data rakenne tiedostosta jos ei tiedostoa niin kopioidaan ladattu rakenne
try:
  with open("data.json") as f:
    data_f = json.load(f)
except:
  data_f = data
  with open(my_file, "w") as f:
    f.write(json.dumps(data_f))

#Flaski flaskaa
app = Flask(__name__)
  
#vt1 pääpalikka, ottaa vastaan erilaisia argumentteja ja niistä riippuen toimii eri tavoin
@app.route('/')
@app.route('/vt1')
def vt1():
  palautus = "" 

  #Parametrit joukkueen lisäämiseen
  nimi   = request.args.get( "nimi", default = "", type = str)
  sarja  = request.args.get("sarja", default = "", type = str)
  idU    = request.args.get(   "id", default ="0", type = str)
  jasenet     = request.args.getlist("jasen")
  leimaustapa = request.args.getlist("leimaustapa")

  #reset kertoo mistä tietorakenteesta esitettävä data näytetään, oletus 0 
  # 0 -> tallennettu rakenne, 1 -> ladattu rakenne
  reset = request.args.get("reset", default = 0, type = int)

  #tila kertoo lisätäänkö vai poistetaanko joukkue
  #oletuksena lisätään, mutta jos tila = delete niin poistetaan
  tila = request.args.get("tila", default = "insert", type = str)

  #valitsee käytössä olevan data_n
  if (reset == 1):
    data_n = data
  else: 
    data_n = data_f

  #päivittää joukkueen tiedot ja palaa "etusivulle"
  if(tila == "update"):
    #print("jee")
    update(data_n, nimi, sarja, jasenet, leimaustapa, idU)
    with open(my_file, "w") as f:
      f.write(json.dumps(data_n))
    return redirect(url_for('vt1'))

  #lisää tai poistaa joukkueen ja palaa "etusivulle" 
  if (nimi != "" and sarja != ""):
    #4h sarjalle
    if (sarja == "4h" or sarja == "4H"):
      if(tila == "delete"):
        i = 0
        for val in data_n["sarjat"][0]["joukkueet"]:
          if(val["nimi"] == nimi):
            data_n["sarjat"][0]["joukkueet"].pop(i)
          i += 1
      if(tila == "insert"):  
        data_n["sarjat"][0]["joukkueet"].append(tee_joukkue(nimi, jasenet, leimaustapa, data_n))
    #2h sarjalle  
    if (sarja == "2h" or sarja == "2H"):
      if(tila == "delete"):
        i = 0
        for val in data_n["sarjat"][1]["joukkueet"]:
          if(val["nimi"] == nimi):
            data_n["sarjat"][1]["joukkueet"].pop(i)
          i += 1
      if(tila == "insert"): 
        data_n["sarjat"][1]["joukkueet"].append(tee_joukkue(nimi, jasenet, leimaustapa, data_n))
    #8h sarjalle
    if (sarja == "8h"  or sarja == "8H"): 
      if(tila == "delete"):
        i = 0
        for val in data_n["sarjat"][2]["joukkueet"]:
          if(val["nimi"] == nimi):
            data_n["sarjat"][2]["joukkueet"].pop(i)
          i += 1
      if(tila == "insert"):  
        data_n["sarjat"][2]["joukkueet"].append(tee_joukkue(nimi, jasenet, leimaustapa, data_n))
   
    #return nimi + " " + tila
    with open(my_file, "w") as f:
      f.write(json.dumps(data_n))
    return redirect(url_for('vt1'))
    
  #Liittää palautettavat rakenteet palautukseen
  palautus += nimet(data_n)
  palautus += rastit(data_n) 
  palautus += "----- taso 3 ----- \n"
  palautus += taso_kolme(data_n)
  palautus += "----- taso 5 ----- \n"
  palautus += tasoviisi(data_n)

  return Response(palautus, mimetype="text/plain;charset=UTF-8")

#esittää tallenetun tietorakenteen
@app.route('/data.json')
def alku_data():
    return data_f

#eesittää alkuperäisen data-tietorakenteen
@app.route('/original.json')
def kopio_data():
    return data

#palauttaa joukkuerakenteen, jonka voi lisätä tietorakenteeseen
def tee_joukkue(joukkue, jasenet, leimaustapa, data_n):
  id_j = 0
  for i in range (3):
    for val in data_n["sarjat"][i]["joukkueet"]:
      if(id_j <= val["id"]): id_j = val["id"] + 1

  return {
        "id": id_j,
        "jasenet": jasenet,
        "leimaustapa": leimaustapa,
        "nimi": joukkue,
        "rastit": []
  }

#päivittää ja tallentaa tietorakenteen (tarvittaessa) ja palaa "etusivulle"
def update(data_n, nimi, sarja, jasenet, leimaustapa, id_j):
  sarja_indeksi = 2
  if(sarja == "4h" or sarja == "4H"):sarja_indeksi = 0
  if(sarja == "2h" or sarja == "2H"):sarja_indeksi = 1

  uusi = tee_joukkue(nimi, jasenet, leimaustapa, data_n)
  uusi["id"] = id_j

  print("haku: " + id_j)

  for i in range (3):
    j = 0
    for val in data_n["sarjat"][i]["joukkueet"]:
      print(str(val["id"]))
      if(id_j == str(val["id"])):
        
        if (nimi == ""): uusi["nimi"] = val["nimi"]
        if (len(jasenet) == 0): uusi["jasenet"] = val["jasenet"]
        if (len(leimaustapa) == 0): uusi["leimaustapa"] = val["leimaustapa"]
        uusi["rastit"] = val["rastit"]

        data_n["sarjat"][i]["joukkueet"].pop(j)
        
        data_n["sarjat"][sarja_indeksi]["joukkueet"].append(uusi)
        print(uusi["nimi"])
        with open(my_file, "w") as f:
          f.write(json.dumps(data_n))
        return redirect(url_for('vt1'))
        #return data_n
      j += 1

  return redirect(url_for('vt1'))

#Palauttaa joukkeiden nimet aakkosjärjestyksessä
def nimet(data_n):
  kaikkilista = []
  kaikkinimet = ""
  
  for i in range (3):
    for val in data_n["sarjat"][i]["joukkueet"]:
      kaikkilista.append(val["nimi"])

  sortattulista = sorted(kaikkilista, key= str.casefold)
  for val in sortattulista:
    kaikkinimet += val + "\n"

  return kaikkinimet

#Palauttaa rastit jotka alkavat numerolla
def rastit(data_n):
  kaikkirastit = ""
  kaikkirastitL = []

  for val in data_n["rastit"]:
    kaikkirastitL.append(val["koodi"])

  kaikkirastitL.sort
  for val in kaikkirastitL:
    if(val != "MAALI" and val != "LAHTO"): kaikkirastit += val + ";"
  kaikkirastit += "\n"
  return kaikkirastit

#Palauttaa tason kolme tulosteen 
def taso_kolme(data_n):
  palautus = ""
  joukkueet = []

  for i in range (3):
    for val in data_n["sarjat"][i]["joukkueet"]:
      joukkue = val["nimi"]
      jasenet = sorted(val["jasenet"], key= str.casefold) 
      pisteet = laske_pisteet(val["rastit"], data_n["rastit"])

      joukkueet.append([joukkue, jasenet, pisteet])
      
  sortedJoukkueet = sorted(joukkueet, key=lambda x: x[2], reverse=True)

  for val in sortedJoukkueet:
    palautus += val[0] + " (" + str(val[2]) + " p)" + "\n" 
    for val_j in val[1]:
      palautus += "    " + val_j + "\n"

  return palautus

#laskee joukkueen pisteet
def laske_pisteet(j_rastit, k_rastit):
  pisteet = 0
  p_rastit = []

  lahtokoodi = ""
  maalikoodi = ""
  for val in k_rastit:
    if(val["koodi"] == "MAALI"): maalikoodi = str(val["koodi"])
    if(val["koodi"] == "LAHTO"): lahtokoodi = str(val["koodi"])

  #Käydään läpi joukkueen rastit ja karsitaan niistä ne jotka eivät ole lähdön ja maalin sisässä
  matkalla = True 
  for val in j_rastit:
    if(val["rasti"] == lahtokoodi):
      p_rastit = []
      matkalla = True
    if(val["rasti"] == maalikoodi):
      matkalla = False
    if(matkalla):
      p_rastit.append(str(val["rasti"]))

  #poistetaan tuplat
  setRastit = set(p_rastit)

  #Pisteytetään pisteiden arvoiset rastit
  for val_j in setRastit:
      for val_k in k_rastit:
        if(val_j == str(val_k["id"])):
          n = val_k["koodi"][0]
          if(is_integer(n)):
            pisteet += int(n)

  return pisteet

#Palauttaa tason kolme tulosteen 
def tasoviisi(data_n):
  palautus = ""
  joukkueet = []

  for i in range (3):
    for val in data_n["sarjat"][i]["joukkueet"]:
      joukkue = val["nimi"]
      jasenet = sorted(val["jasenet"], key= str.casefold) 
      pisteet = laske_pisteet(val["rastit"], data_n["rastit"])
      tulos = laske_pisteetEtaJaAika(val["rastit"], data_n["rastit"])

      joukkueet.append([joukkue, jasenet, pisteet, tulos])
      
  sortedJoukkueet = sorted(joukkueet, key=lambda x: x[2], reverse=True)

  for val in sortedJoukkueet:
    palautus += val[0] + str(val[3]) + "\n" 
    for val_j in val[1]:
      palautus += "    " + val_j + "\n"

  return palautus

#laskee joukkueen pisteet
def laske_pisteetEtaJaAika(j_rastit, k_rastit):
  alkuaika  = "2017-03-18 12:00:00"
  loppuaika = "2017-03-18 12:00:00"
  pisteet = 0
  p_rastit = []

  lahtokoodi = ""
  maalikoodi = ""
  for val in k_rastit:
    if(val["koodi"] == "MAALI"): maalikoodi = str(val["id"])
    if(val["koodi"] == "LAHTO"): lahtokoodi = str(val["id"])

  #Käydään läpi joukkueen rastit ja karsitaan niistä ne jotka eivät ole lähdön ja maalin sisässä
  matkalla = True 
  for val in j_rastit:
    if(str(val["rasti"]) == lahtokoodi):
      p_rastit.clear()
      matkalla = True
      alkuaika = str(val["aika"])
      
    if(str(val["rasti"]) == maalikoodi):
      matkalla = False
      loppuaika = str(val["aika"])

    if(matkalla):
      p_rastit.append(str(val["rasti"]))

  #lasketaan aika
  aika = ajankulu(alkuaika, loppuaika)

  #poistetaan tuplat
  setRastit = set(p_rastit)

  lat = ""
  lon = ""

  matka = 0.0

  #Pisteytetään pisteiden arvoiset rastit ja lasketaan etäisyys
  for val_j in setRastit:
      for val_k in k_rastit:
        if(val_j == str(val_k["id"])):
          n = val_k["koodi"][0]

          if(is_integer(n)):
            pisteet += int(n)

          if(lat != ""):
             matka += etaisyys(val_k["lat"], val_k["lon"], lat, lon)

          lat = val_k["lat"]
          lon = val_k["lon"]
            
  
  return " (" + str(pisteet) + " p, " + str(int(matka)) + " km, " + str(aika) + ")"

#laskee etäisyyden kahden gps kordinaatin välillä
def etaisyys(lat11, lon11, lat22, lon22):

  R = 6373.0

  lat1 = radians(float(lat11))
  lon1 = radians(float(lon11))
  lat2 = radians(float(lat22))
  lon2 = radians(float(lon22))

  dlon = lon2 - lon1
  dlat = lat2 - lat1

  a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
  c = 2 * atan2(sqrt(a), sqrt(1 - a))
  
  return R * c #Palautus on liian suuri en tiedä miksi

#laskee kahden ajanjakson välissä kuluneen ajan
def ajankulu(aika1, aika2):
  if(aika1 == aika2):
    return "00:00:00"
  
  t1 = timedelta(hours= int(aika1[10:13]), minutes= int(aika1[14:16]), seconds= int(aika1[17:19]))
  t2 = timedelta(hours= int(aika2[10:13]), minutes= int(aika2[14:16]), seconds= int(aika2[17:19]))

  palautus = str(t2 - t1)
  if(len(palautus) == 7): palautus = "0" + palautus
  return palautus


#onko n kokonaisluku
def is_integer(n):
    try:
        float(n)
    except ValueError:
        return False
    else:
        return float(n).is_integer()

#Aloittaa pyörityksen venvissä. 
if __name__ == '__main__':
  app.run()