Introduction
============

ARFilePreview provides the ability to load a file and have under the download link a preview of the file.
There are 3 views provided in order to have:

* file to download and preview on the same view
* file to download only
* preview only without link to download file ( file shown as web page )

You may add views and/or transforms in order to render different files in a html view.

The preview is based on portal_transforms and can support as many formats as transforms installed.
If you wish to use the new plone.transforms utility, please use the 2.3 branch.

ARFilePReview works fine with FTP, WebDAV and ZopeExternalEditor (all the possibilities of the ATFile
or any content type that provides a IPreviewAware interface. This interface is added to ATFile by ARFilePreview.

Initial concept:

* Ando RAKOTONIRINA, Julien TOGNAZZI - INSERM DSI

Developpers:

* Jean-Nicolas BES - atReal <contact AT atreal.net>
* Matthias BROQUET - atReal <contact AT atreal.net>
* Therry BENITA - atReal <contact AT atreal.net>

Contributors:

* Balazs REE - Greenfinity <ree AT ree.hu>
* Jean-Charles ROGEZ - EDF

Sponsors:

* INSERM DSI - http://www.inserm.fr
* SCET - http://www.scet.fr
* VILLE DE SAVIGNY-SUR-ORGE - http://www.savigny.org
* VILLE D'ISTRES - http://www.istres.fr
