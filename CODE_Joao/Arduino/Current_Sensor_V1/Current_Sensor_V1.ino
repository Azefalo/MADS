#include <EmonLib.h>
#include <LiquidCrystal.h>

// Création de l'objet LCD : RS, E, DB4, DB5, DB6, DB7
//LiquidCrystal lcd(12, 11, 5, 4, 3, 2);

// Création de l'objet EmonLib
EnergyMonitor emon;

// Tension approximative du secteur
#define MAINS_VOLTAGE 230.0

void setup() {
  Serial.begin(9600);

  Serial.println("\nInitializing ...");
  // Initialisation de l'écran LCD
  //lcd.begin(16, 2);
  //lcd.print("Mesure courant...");
  //delay(2000);
  //lcd.clear();

  // Initialisation du capteur SCT013 sur A1 avec un facteur de calibration de 30
  emon.current(A1, 30.0);  // capteur 30A/1V
}

void loop() {
  // Calcul du courant RMS sur 20 demi-cycles (environ 2 secondes)
  emon.calcVI(20, 2000);
  float current = emon.Irms;
  float power = current * MAINS_VOLTAGE;

  // Affichage sur le moniteur série
  Serial.print("Courant: ");
  Serial.print(current, 2);
  Serial.print(" A\tPuissance: ");
  Serial.print(power, 1);
  Serial.println(" W");
/*
  // Affichage sur l'écran LCD
  lcd.setCursor(0, 0);
  lcd.print("Current: ");
  lcd.print(current, 2);
  lcd.print(" A     ");

  lcd.setCursor(0, 1);
  lcd.print("Power: ");
  lcd.print(power, 1);
  lcd.print(" W     ");

  delay(1000);
*/
}