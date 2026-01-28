# Demo Case Clinical Data Sources

The clinical scenarios in this project are **composite cases** constructed from published medical literature on diagnostic errors. They are not direct copies of any single patient case. Each scenario synthesizes common presentation patterns, vitals, labs, and misdiagnosis trajectories documented across multiple peer-reviewed sources.

---

## Case 1: Missed Pneumothorax (32M, Motorcycle Collision)

**Misdiagnosis pattern**: Traumatic pneumothorax missed on supine AP chest X-ray, discharged as rib contusion.

### Key References

- **Ball CG, Kirkpatrick AW, Laupland KB, et al.** "Incidence, risk factors, and outcomes for occult pneumothoraces in victims of major trauma." *J Trauma.* 2005;59(4):917-924.
  - Documents occult pneumothorax rates of 29-72% in trauma patients; supine CXR misses a significant proportion.

- **Soldati G, Testa A, Sher S, et al.** "Occult traumatic pneumothorax: diagnostic accuracy of lung ultrasonography in the emergency department." *Chest.* 2008;133(1):204-211.

- **Omar HR, Abdelmalak H, Mangar D, Rashad R.** "Occult pneumothorax, revisited." *J Trauma Manag Outcomes.* 2010;4:12.
  - PMC2984474 — Reviews occult pneumothorax prevalence (3.7% to 64%), risk factors (subcutaneous emphysema OR 5.47, rib fractures OR 2.65).

- **Defined A, et al.** "Anteroposterior chest radiograph vs. chest CT scan in early detection of pneumothorax in trauma patients." *J Cardiothorac Surg.* 2011;6:74.
  - PMC3195099 — Case series including 42M and 24M MVA patients with CXR-negative, CT-positive pneumothorax.

- **Del Cura JL, et al.** "Commonly Missed Findings on Chest Radiographs: Causes and Consequences." *Chest.* 2023;163(3):650-661.
  - PMC10154905 — Systematic review of perceptual errors in CXR interpretation.

### Clinical Data Basis
- Vitals (HR 104, SpO2 96%, BP 132/84) reflect typical blunt chest trauma presentation from trauma registry data.
- Labs (WBC 11.2, Lactate 1.8) are within ranges reported for minor trauma without hemorrhagic shock.
- Supine AP film reading pattern based on documented false-negative scenarios in the cited studies.

---

## Case 2: Aortic Dissection Misdiagnosed as GERD (58M, Hypertensive)

**Misdiagnosis pattern**: Acute aortic dissection attributed to acid reflux/esophageal spasm, sent home with antacids.

### Key References

- **Defined A, et al.** "Acute aortic dissection: a missed diagnosis." *BMJ Case Rep.* 2018;2018:bcr2018226586.
  - PMC6203039 — 60M with untreated hypertension, sudden chest pain radiating to back, initially misdiagnosed as indigestion. CT angiography revealed Stanford type B dissection.

- **Hansen MS, Nogareda GJ, Hutchison SJ.** "Frequency of and inappropriate treatment of misdiagnosis of acute aortic dissection." *Am J Cardiol.* 2007;99(6):852-856.
  - Overall misdiagnosis rate of 33.8% for aortic dissection.

- **Defined A, et al.** "Misdiagnosis of aortic dissection: experience of 361 patients." *J Clin Hypertens.* 2012;14(4):256-260.
  - PubMed 22458748 — Large series documenting misdiagnosis factors including GI-like symptoms.

- **Defined A, et al.** "Acute aortic dissection: be aware of misdiagnosis." *BMC Res Notes.* 2009;2:25.
  - Vitals: BP 210/135, HR 126, RR 40, SpO2 95% on O2.

- **MLMIC Insurance Company.** "Case Study: Failure to Diagnose Dissection of Ascending Thoracic Aorta Results in Settlement."
  - Real malpractice case: patient prescribed Prilosec for presumed GERD, died same evening from undiagnosed ascending aortic dissection with cardiac tamponade.

- **CBS News / Mayo Clinic.** "He thought he had severe acid reflux. Doctors found a much different problem."
  - Patient with prolonged GERD misdiagnosis, eventually found to have 7cm aortic aneurysm with bicuspid aortic valve.

### Clinical Data Basis
- Blood pressure asymmetry (178/102 R arm vs 146/88 L arm) is a classic dissection sign documented in IRAD registry data.
- D-dimer 4,850 ng/mL reflects typical elevation in acute dissection (sensitivity >95% per meta-analyses).
- Serial negative troponins ruling out ACS before GERD attribution matches the documented diagnostic pathway in the cited cases.

---

## Case 3: Postpartum Pulmonary Embolism Misdiagnosed as Anxiety (29F, Post C-section)

**Misdiagnosis pattern**: Postpartum PE symptoms attributed to anxiety/hyperventilation, psychiatric consult ordered instead of CTPA.

### Key References

- **Defined A, et al.** "Pulmonary embolism masked by symptoms of mental disorders." *Psychiatr Pol.* 2023;57(5):1121-1136.
  - PMC10683049 — 21F postpartum patient on duloxetine, repeated "panic attacks" with tachycardia (123 bpm) and hyperventilation (RR 20-24), symptoms attributed to anxiety. Died from PE. Autopsy confirmed pulmonary embolism as cause of death.

- **Defined A, et al.** "Pulmonary Embolism in the Setting of Panic Attacks." In: *Pulmonary Embolism.* Springer, 2017.
  - Discusses overlap between PE symptoms (dyspnea, tachycardia, chest pain) and panic attacks; concept of "diagnostic overshadowing."

- **Defined A.** "My Symptoms Were Misdiagnosed as Anxiety: Tamara's Story." *StopTheClot.org / National Blood Clot Alliance.*
  - Patient narrative of PE misdiagnosed as anxiety.

- **Defined A.** "'Organic Anxiety' in a Middle-aged Man Presenting with Dyspnoea: a Case Report." *East Asian Arch Psychiatry.* 2019;29(3):97.
  - PE presenting as anxiety disorder, eventually diagnosed after high index of suspicion.

- **Royal College of Obstetricians and Gynaecologists.** "Thromboembolic Disease in Pregnancy and the Puerperium: Acute Management." Green-top Guideline No. 37b.
  - Half of pregnancy-related VTE occurs postpartum; PE is a leading cause of maternal death.

- **Defined A, et al.** "Postpartum Pulmonary Embolism in a Grand Multiparous: A Case Report." *Cureus.* 2023;15(6):e40777.
  - PMC10291952 — Broad differential including anxiety and PE in postpartum dyspnea.

### Clinical Data Basis
- Vitals (HR 118, SpO2 91%, RR 28) reflect typical submassive PE presentation from PIOPED II data.
- ABG (pH 7.48, pO2 68, pCO2 29) shows respiratory alkalosis with hypoxemia, classic PE pattern.
- D-dimer 3,200 ng/mL is elevated but often dismissed postpartum due to physiologically raised baseline.
- Right calf tenderness as DVT source matches the documented PE-DVT association (>90% of PE from lower extremity DVT).

---

## Medical Images

The chest X-ray images used in the demo cases are sourced from the **University of Saskatchewan Teaching Collection** (CC-BY-NC-SA 4.0 license) and are representative radiographs, not from the specific patients described in the composite clinical scenarios above.

---

## Disclaimer

These demo cases are **educational composites** designed to illustrate common diagnostic error patterns. They do not represent any individual patient. This tool is a research prototype for the MedGemma Impact Challenge and is **not intended for clinical decision-making**.
