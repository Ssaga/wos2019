==== OVERVIEW ====
The python script orbitGMAT.py is used to control the satellite simulation software GMAT.

Functionally, the python script executes the following steps:
1) edits the mission script WOS_template.script and saves the editted copy in another file location
2) executes GMAT software and runs the edited mission script. The mission script initialises all aspects of the mission, including satellite orbit. The script also commands GMAT to output relevant satellite parameters (LLA, vel, ECEF) into text files
3) The python script reads the generated text files and processes them into a boolean mask, indicating swath visible in the area of ops

==== INSTALLATIOn ====
1) Install GMAT (https://sourceforge.net/projects/gmat/files/GMAT/GMAT-R2018a/)

2) Place WOS_template.script into ~\GMAT\2018a\bin\

3) To run, call the python function playGame(a, e, i, om, Om, gam, isRHS, isSAR)