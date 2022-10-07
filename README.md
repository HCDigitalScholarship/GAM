<img style="border-bottom: 2px solid #ffec00; padding-top: 8px;" height= "200" width="200" src="https://github.com/HCDigitalScholarship/GAM/raw/master/gam_app/static/Logo_01.png" alt="GAM logo"/></a><br>

[![License: CC BY-NC-SA 4.0](https://licensebuttons.net/l/by-nc-sa/4.0/80x15.png)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

Los Archivos Digitales del Grupo de Apoyo Mutuo <br>
Digital Archives of the Group of Mutual Assistance (Guatemala) <br>
  
https://archivogam.haverford.edu/  

## GAM's History
>El Grupo de Apoyo Mutuo es una organización de la sociedad civil sin fines de lucro creada en 1984 que aglutina a los familiares de personas detenidas ilegalmente y desaparecidas forzadamente en Guatemala durante el Conflicto Armado Interno que duró de 1960 a 1996. Nuestro ámbito de trabajo abarca la justicia por el desaparecido y la dignificación de las víctimas, trabajo que ha llevado a GAM a estar nominado por el Premio Nobel de la Paz en 1986. Además elaboramos informes temáticos relacionados a los índices de violencia actuales y   monitoreo a las instituciones que conforman el sector de seguridad y justicia.

<p>In 1984, the friends and family members of Guatemalans ‘disappeared’ by state security forces formed the Grupo de Apoyo Mutuo (GAM). Members of the GAM searched for their loved ones and demanded information from state officials during a period of Cold War violence in which Guatemala’s military and police routinely murdered activists, union leaders, agricultural workers, and anyone deemed an insurgent or subversive threat. In the countryside, the military waged a genocidal campaign against indigenous Guatemalan communities in an effort to combat guerrilla forces by taking “the water away from the fish.” The Guatemalan Truth Commission’s 1999 <a href="https://www.usip.org/publications/1997/02/truth-commission-guatemala">report</a> documented over 200,000 deaths during internal conflict (1960-1996) and attributed 93% of human rights violations to state security and related paramilitary forces. The GAM has spent the past three decades collecting textual, visual, and audio-materials related to ongoing human rights trials and historical memory.</p>

<p><img src="http://ds.haverford.edu/gam-archive/images/marcha.jpg" alt="GAM members marching with posters of disappeared victims)" height="520.44" width="740"/><br>
<em>GAM members marching with posters of disappeared victims (Photo courtesy of Pat Goudvis).</em></p>

<p>In 2016, Anita Isaacs - a political science professor at Haverford College who researches transitional justice in Guatemala and has provided expert testimony in human rights trials - made one of her regular visits to the GAM offices. There, GAM staff showed Anita the progress they were making on their new project to catalog their materials and create an archive. With funding from the German Corporation for International Cooperation (GIZ) and in collaboration with the Archivo Histórico de la Policía Nacional (AHPN) the GAM formed an archival team and cleaned, organized, and cataloged a large portion of the materials they had collected over three decades. Anita consulted with librarians at Magill Library at Haverford College about the possibility of supporting the GAM’s digitization efforts in the fall of 2016. Haverford librarians successfully applied for a CLIR Postdoctoral Fellow in Data Curation for Latin American and Caribbean Studies. In the summer of 2017 they hired me, Alex Galarza, to lead the project.</p>

<p>This is a collaborative, post-custodial digitization project that aims to preserve and provide access to materials held by Guatemala’s oldest human rights organization. Over the past four months, <a href="http://ds.haverford.edu/gam-archive/people/">we</a> have successfully implemented a digitization workflow and begun building a public web platform to preserve and share materials. I took two trips this fall to Guatemala City to learn more about the collection and the GAM’s approach to issues of privacy, security, and ethics in digitizing and sharing sensitive materials. We have also created opportunities for student research and co-curricular learning in addition to the integration of materials into classes to be taught at Haverford.</p>

<p>Our digitization workflow consists of scanning equipment, a secure file transfer protocol, and a descriptive workflow for metadata. Building this capacity has allowed the project team to begin work on cataloging and digitizing around 4,000 cases of disappearances which contain roughly 8 linear meters (26 linear feet) of documentation. The size and nature of case files vary wildly, with some containing only handwritten fieldnotes of testimonies of rural massacres while others contain hundreds of pages of detailed description, news clippings, and letter writing campaigns.</p>

## Local Development
### Clone the repo

`git clone https://github.com/HCDigitalScholarship/GAM.git`

### Install the requirements

`pip install virtualenv`

`python3 -m venv env`

`source env/bin/activate`

`python -m pip install --upgrade pip`

`pip install -r requirements.txt`


### Set up a local server

`python manage.py migrate`

`python manage.py runserver`

View local server at: http://127.0.0.1:8000/

## Deploying

Start by ssh-ing into the server (`ssh USER@IP_ADDRESS`). (To deploy to production, you must be on the [Haverford VPN](https://iitskb.sites.haverford.edu/knowledge-base/installing-the-vpn-client/) first. Request credentials from IT if you don't have them.)

The project's source code is located in "/srv/GAM". You can access it and pull the most up-to-date version from Github using:

`cd /srv/GAM`

`git pull origin master`

Note: you can use `sudo` before any command to get elevated privileges for anything that might require them.

## Summer 2022 Updates
### Search Functionality Improvements
- In the previous version of the website, basic search was implemented which only allow us to perform exact matches. Therefore, basic search has several limitations especially when you want to perform complex lookups.
- In the new version, full-text search was implemented which offers huge improvements over basic search.
- To leverage full-text search, the entire database had to be converted from MySQL to PostgreSQL.
- Some of the improvements that full-text search offers:
  - Stop words such as (“a”, “an”, and “the”) are ignored. “The military station” returns same results as “military station”. On the other hand, basic search just returns the results that only includes “The military station”.
  - Since search queries go through a stemming algorithm in full-text search, similar words (such as singular vs plurals and unaccented vs accented names) will be treated as similar words. Therefore, “Velasquez”, “Velásquez” return the same results
  - Search results are ordered by relevancy. It takes into account how often the query terms appear in the document, how close the terms are on the document, and how important the part of the document is where they occur.
- Full-text search Django's documentation can be found here: https://docs.djangoproject.com/en/4.1/ref/contrib/postgres/search/



