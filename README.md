<p align="center">
  <img src="https://borraryestudiar.lucasgrasso.com.ar/logo.png" style="width:200px;height;200px"/>
</p>
<h1 align="center">EliminarRtasdeParciales</h1>

![python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

API EliminarRtasdeParciales (https://api.eliminarrtas.lucasgrasso.com.ar/). Server AGSI basado en [Sanic](https://sanic.dev/en/) y [Uvicorn](https://www.uvicorn.org/).

Usable en https://borraryestudiar.lucasgrasso.com.ar/ , [Repo a la aplicacion](https://github.com/LucasGrasso/EliminarRtasDeParciales-App/)
 
 Elimina respuestas dadas en un array de strings "search_strings" y el subrallado amarillo del pdf "file".
 
 endpoints:  
  * "/": root.  
  * "/eraseAnswers": Elimina las respuestas. Se le debe pasar un array de strings a borrar bajo "search_strings" y un archivo PDF valido bajo "file" en un FormData.

 
 __El PDF DEBE ser de texto, sino el progama no funciona correctamente__  
 
 ## Ejemplos:  
 [Parcial Con respuestas](https://borraryestudiar.lucasgrasso.com.ar/pruebas/Parcial_ICSEValdez.pdf)(Pasandole que borre V,F,X,GE,TE,II,IF)   
 [Parcial Sin respuestas](https://borraryestudiar.lucasgrasso.com.ar/pruebas/Parcial_ICSEValdez_SinCorrecciones.pdf)
 
_Creditos a la catedra Valdez de ICSE(Introducción al Conocimiento de la Sociedad y Estado), CBC/UBAXXI UBA, por los parciales usados para ejemplificar el uso de la aplicación_
