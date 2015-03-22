This project is aimed to develop editor, that significantly simplifies annotation process of transcribed spoken dialog. Annotation process was developed to maximize inter-annotator agreement and annotation reliability. Editor helps annotator to speed up annotation process and to correct their typos and semantical nonsense in annotations.

# Developers #

CORE development (c) 2005-6 [Filip Jurčíček](http://filip.jurcicek.googlepages.com/), Jiří Zahradil, Libor Jelínek

Signed language support (c) 2006 Jakub Kanis (with some core mods)

# Main Publications #

a, Jurcicek F., Zahradil J., Jelinek L.: A Human-Human Train Timetable Dialogue Corpus, EUROSPEECH 2005, Lisboa, Portugal. [Download PDF](http://filip.jurcicek.googlepages.com/jurcicek05human.pdf)

> This paper describes progress in a development of the human-human dialogue corpus. The corpus contains transcribed user's phone calls to a train timetable information center. The phone calls consist of inquiries regarding their train traveler's plans. The corpus is based on dialogues's tran­scription of user's inquiries that were previously collected for a train timetable information center. We enriched this transcription by dialogue act tags. The dialogue act tags comprehend abstract semantic annotation. The corpus comprises a recorded speech of both operators and users, orthographic transcription, normalized transcription, normalized transcription with named entities, and dialogue act tags with abstract semantic annotation. A combination of a dialogue act tagset and a abstract semantic annotation is proposed. A technique of dialogue act tagging and abstract semantic annotation is described and used.

b, Jurcicek F., Zahradil J., Šmídl L.: Prior of the Lexical model in the Hidden Vector State Parser, SPECOM 2006, St.Petersburg, Russia. [Download PDF](http://filip.jurcicek.googlepages.com/jurcicek06prior.pdf)

> This paper describes an implementation of a statistical semantic parser for a closed domain with limited amount of training data. We implemented the hidden vector state model, which we present as a structure discrimination of a flat-concept model. The model was implemented in the graphical modeling toolkit. We introduced into the hidden vector state model a concept insertion penalty as a part of pattern recognition approach. In our model, the linear interpolation was used for both to deal with unseen words (unobserved input events) in training data and to smooth probabilities of the model. We evaluated the implementation of the concept insertion penalty in our model on a closed domain human-human train timetable dialogue corpus. We found that the concept insertion penalty was indispensable in our implementation of the hidden vector state model on the human-human train timetable dialogue corpus. Accuracy of the baseline system was increased from 33.7% to 55.4%.

c, Jakub Kanis, Jiří Zahradil, Filip Jurčíček, and Luděk Müller: Czech-Sign Speech Corpus for Semantic based Machine Translation, TSD 2006, Brno, Czech Republic. [Download PDF](http://filip.jurcicek.googlepages.com/kanis06czech.pdf)

> This paper describes progress in a development of the human-human dialogue corpus for machine translation of spoken lan- guage. We have chosen a semantically annotated corpus of phone calls to a train timetable information center. The phone calls consist of inquiries regarding their train traveler plans. Corpus dialogue act tags incorporate abstract semantic meaning. We have enriched a part of the corpus with Sign Speech translation and we have proposed methods how to do au- tomatic machine translation from Czech to Sign Speech using semantic annotation contained in the corpus.

d, Zdeněk Krňoul, Jakub Kanis, Miloš Železný, Luděk Müller and Petr Císař: 3D Symbol Base Translation and Synthesis of Czech Sign Speech, SPECOM 2006, St.Petersburg, Russia. [Download PDF](http://ui.zcu.cz/projects.old/dae/download/zkjk-specom2006.pdf)

> This paper presents primary results of translation spoken Czech to Signed Czech and a synthesis of signs by the computer animation. The synthesis of animation employs a symbolic notation. An automatic process of synthesis generates the articulation of hands from this notation. The translation system is built on the statistical ground. For the notation of the new signs, the graphic editor is designed.


# Installation #

Editor is developed in Python language, as result, it is truly multiplatform. It takes advantage of multiplatform wxWindows windowing toolkit that simplifies and enriches GUI of editor.

In general, DAE installation procedury is simple xcopy – just copy all files to your disk and change your settings.xml file according to documentation.

For your conveniance, we publish exe versions compiled

You needs this software installed before:

  * Python 2.4
  * wxPython, we use 2.6 unicode, we recommended to use the latest version
  * for Windows, there is an alternative, you can install PyWin32 2.04. This package installs additional packages you might need.
  * for compiling to EXE under Windows, install Py2Exe and use make-exe.bat makefile, included with sources.

# License #

You can download full text of DAE License. Briefly, DAE is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

DAE is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111–1307 USA

# Corpus #

Corpus structure is derived from DATE format (XML) – for more information please see our EuroSpeech 2005 paper. If you have any other questions, you can contact us.

Same sample data are stored in the data ;-) directory.

# Documentation #

Documentation is rather short at this moment.

  1. There is a Czech annotation manual (280 kB, PDF) for semantic annotation, unfortunately we do not have an English version. Manual can be slightly out-of-date.
  1. There is also a Czech translation manual (315 kB, PDF) for people who did translation from Czech to Signed czech. This manual very precisely describes all translation-related features.
  1. There is english description of the annotation scheme in the Ph.D. thesis Jurčíček, F.: [Statistical approach to the semantic analysis of spoken dialogues](http://filip.jurcicek.googlepages.com/jurcicek07statistical.pdf). In: Dizertační práce (Ph.D. thesis). Západočeská univerzita v Plzni, Fakulta aplikovaných věd, 2007.

Dialog data format is compatible with DATE format (Walker, M., and Passonneau, R., DATE: A Dialogue Act Tagging Scheme for Evaluation of Spoken Dialogue Systems, IEEE Trans. Speech and Audio Proc., 7(6):697--708, 1999.)

# References #

The DAE editor is used in these projects:

  * [Extended HVS parser](http://code.google.com/p/extended-hidden-vector-state-parser/)
  * [MUSSLAP Project](http://musslap.zcu.cz/en/about-project/)