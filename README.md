<p align="center">
  <a href="" rel="noopener">
 <img width=500px height=300px src="https://www.euspa.europa.eu/sites/default/files/styles/news_640x480_retinafy/public/files/content/news/images/home/osnma-news.jpg?itok=2u1UslSa" alt="Image property of EUSPA"></a>
</p>

<h3 align="center">OSNMA for Galileo Mass-Market GNSS Receivers<sup>1</sup></h3>

<div align="center">

[![Status](https://img.shields.io/badge/status-In_progress-success.svg)]()

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](/LICENSE)

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

</div>

---


[OSNMA](https://gssc.esa.int/navipedia/index.php/Galileo_Open_Service_Navigation_Message_Authentication) is one of Europe's [Galileo](https://www.euspa.europa.eu/european-space/galileo/What-Galileo) coolest features: the authentication of GNSS Data. Devices such as Drones rely on having accurate not spoofed data, and as rapid as its market grows, as rapid grows the need of having anti-spoofing mechanisms.
You can find that there are already spoofing detection mechanisms,  but there is still no mechanism that can ensure GNSS data has not been altered for cheap mass-market standalone GNSS Receivers that does not rely on on-line authentication.
OSNMA is the unique Galieo GNSS feature that allows any receiver to make sure the data it is receiving has not been altered. OSNMA is expected to be one extra layer of security that can work together with other anti-spoofing/anti-jamming techniques.

This library provides any user the means to implement OSNMA **in mass market receivers** that can be bought for really cheap -[e.g., this NEO-M9N](https://www.mikroe.com/gnss-7-click). Specifically, this library has been developed based on Ublox Receivers, altough its core can work for any GNSS receivers that can get Galileo I/NAV Pages.

*Note: the work in this library is not related to ublox as a company, we only use their products as they are well-documented and cost-effective. UBLOX is a trademark of u-blox Holding AG.*
## 📚 Applicable Documentation <a name = "about"></a>

The following documents have been used to prepare this library, although you can find related info in our [/docs/](https://github.com/astromarc/osnmaPython/tree/master/docs) section.

For GALILEO's documentation, please find last issues on [GSC site](https://www.gsc-europa.eu/electronic-library/programme-reference-documents).

For UBLOX documentation, please find updated documents on their [webpage](https://www.u-blox.com/en/product-resources)

```
AD.1 The European GNSS (Galileo) Open Service Navigation Message Authentication (OSNMA) User Interface Control Document for the Test Phase 
Short title: OSNMA User ICD for the Test Phase
Issue: 1.0
```
```
AD.2 The European GNSS (Galileo) Open Service Signal-In-Space Interface Control Document
Short Title: OS SIS ICD
Issue: 2.0
```
```
AD.3 NEO-M9N - Standard precision GNSS module - Integration manual
Short Title: NEO-M9N Integration Manual
Reference: UBX-19014286
Issue: R06
```

## 🏁 Getting Started <a name = "getting_started"></a>

TBW

### Prerequisites

This could should work at for any python3. It has been tested for python 3.10.

The library uses several in-build librarys but the following external are needed:

1. pyserial:
```
pip install pySerial  
```
2. pyubx2:
```
pip install pyubx2 
```
3. ecdsa:
```
pip install ecdsa 
```
### Installing


## ✍️ Authors <a name = "authors"></a>

- [@jametller](https://github.com/jametller) - GNSS & Cryptography Expert
- [@astromarc](https://github.com/astromarc) - GNSS Engineer




* * *
<sup>1</sup>Cover image is property of [EUSPA](https://www.euspa.europa.eu/)
