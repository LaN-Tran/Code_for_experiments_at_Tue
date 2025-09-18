- 0. Prerequisites before using and understanding the codes in this repository, visit: https://github.com/LaN-Tran/Automate_Lab_Instrument 

- 1. Setup TCP/IP for keithley SMU: follow **Series 2600B System SourceMeter® instrument Reference Manual - Section 8: Instrument programming -LAN cable connection** to setup the **Auto method** for **LAN config**

- 2. Configure NI-MAX to find TCP/IP of Keithley SMU through LAN cable, [link](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000x3gXCAQ&l=nl-NL) or [link](https://documentation.omicron-lab.com/BodeAutomationInterface/3.24/articlesScpi/general/setupConnection.html?tabs=setup-csharp)

- 3. `keithley2600` library works with LAN cable connection (TCP/IP) as well:

```
k = Keithley2600('TCPIP0::169.254.0.1::inst0::INSTR', visa_library = 'C:/windows/System32/visa64.dll', timeout = 10000)
```

- 4. references for sending tsp scripts to smu:

  - 4.1 https://www.tek.com/en/documents/application-note/how-to-write-scripts-for-test-script-processing-(tsp)

  - 4.2 https://www.tek.com/en/products/software/tsp-toolkit-scripting-tool

  - 4.3 https://github.com/tektronix/keithley/tree/main