# Overview

The Python control layer for the ESA DTE-S2GOS synthetic scene generator service

![logo.svg](assets/logo.svg){ .centered-logo width="300"}

_Note, the S2GOS controller project and its documentation are still in an early 
development stage._

## Project Overview

The _Digital Twin Earth Synthetic Scene Generator and Observation Simulator_ 
(DTE-S2GOS) project consists in the development of a new component of the 
[ESA Destination Earth Initiative](https://destination-earth.eu/) 
to be implemented in the [ESA DestinE Platform](https://platform.destine.eu/) 
as a pre-operational service. The primary objective of DTE-S2GOS is to develop a 
comprehensive and accurate simulation framework that can generate physically 
realistic synthetic 3D scenes of the Earth and simulate ground-based or spaceborne 
remote sensing observations, among other with the 
[Eradiate Radiative Transfer Model](https://github.com/eradiate/eradiate).

[The Project](https://dte-s2gos.rayference.eu/about/){ .md-button .md-button--primary }

## Controller Overview

This project hosts two Python packages:

* `s2gos-client` - CLI, GUI, and API clients that allow for interaction 
  with the S2GOS scene simulator service.  
* `s2gos-server` - a FastAPI-based implementation of the 
  [OGC API - Processes](https://ogcapi.ogc.org/processes/) that is wrapped around
  the S2GOS scene simulator service based on [Apache Airflow](https://airflow.apache.org/).

The development of the S2GOS controller paved the way for the development of the more 
general [Eozilla Suite](https://eo-tools.github.io/eozilla/) of tools supporting the 
interaction with EO workflow orchestration and processing systems. The S2GOS controller 
therefore build on the Eozilla packages 
[Cuiman](https://github.com/eo-tools/eozilla/tree/main/cuiman), 
[Wraptile](https://github.com/eo-tools/eozilla/tree/main/wraptile) and others.

[Get Started](installation){ .md-button .md-button--primary }
